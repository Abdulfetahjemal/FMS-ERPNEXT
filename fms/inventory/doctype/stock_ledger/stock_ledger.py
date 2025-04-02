# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockLedger(Document):
    def on_submit(self):
        """On Stock Ledger submit, update or create Stock Ledger Entries."""
        self.process_stock_ledger_entries()

    def on_cancel(self):
        """On Stock Ledger cancel, cancel the linked Stock Ledger Entries."""
        self.process_stock_ledger_entries(cancel=True)

    def on_trash(self):
        """On Stock Ledger trash, delete the linked Stock Ledger Entries."""
        self.process_stock_ledger_entries(delete=True)

    def before_save(self):
        """Before saving, temporarily store the qty_change value."""
        for item_data in self.item_info:
            item_data._temp_qty_change = item_data.quantity

    def on_update(self):
        """On Stock Ledger update, update the Stock Ledger Entries."""
        self.process_stock_ledger_entries()

    def after_insert(self):
        """After inserting, update the Stock Ledger Entries."""
        frappe.msgprint("Stock Ledger Entry has been saved successfully.")
        self.process_stock_ledger_entries()

    def process_stock_ledger_entries(self, cancel=False, delete=False):
        """
        Processes Stock Ledger Entries by updating existing ones or creating new ones.
        Handles cancel and delete scenarios.
        """
        try:
            existing_entries = self.get_existing_entries()
            existing_entry_names = {entry["name"] for entry in existing_entries}

            for item_data in self.item_info:
                self.handle_item_entry(item_data, existing_entry_names, cancel, delete)

            self.handle_orphaned_entries(existing_entry_names, cancel, delete)
        except Exception as e:
            frappe.log_error(f"Error processing Stock Ledger Entries: {e}", "Stock Ledger")
            frappe.msgprint("Error processing Stock Ledger Entries. Check logs.")
            raise

    def get_existing_entries(self):
        """Fetches existing Stock Ledger Entries linked to this Stock Ledger."""
        return frappe.get_all(
            "Stock Ledger Entry",
            filters={"stock_ledger": self.name},
            fields=["name"]
        )

    def handle_item_entry(self, item_data, existing_entry_names, cancel, delete):
        """Handles the creation or update of a Stock Ledger Entry for an item."""
        item_code, warehouse, qty_change = item_data.item, item_data.warehouse, item_data.quantity
        previous_qty_change = getattr(item_data, "_temp_qty_change", None)

        # Adjust qty_change and previous_qty_change for Stock Out
        if self.type == "Stock Out":
            qty_change *= -1
            if previous_qty_change is not None:
                previous_qty_change *= -1

        matching_entry_name = frappe.db.get_value(
            "Stock Ledger Entry",
            {"stock_ledger": self.name, "item_code": item_code, "warehouse": warehouse}
        )

        if matching_entry_name:
            self.update_stock_ledger_entry(matching_entry_name, qty_change, cancel, delete, previous_qty_change)
            existing_entry_names.discard(matching_entry_name)
        elif not cancel and not delete:
            self.create_stock_ledger_entry(item_code, warehouse, qty_change)

    def update_stock_ledger_entry(self, entry_name, qty_change, cancel=False, delete=False, previous_qty_change=None):
        """Updates an existing Stock Ledger Entry."""
        stock_entry = frappe.get_doc("Stock Ledger Entry", entry_name)
        if cancel:
            stock_entry.cancel()
        elif delete:
            stock_entry.delete()
        else:
            stock_entry.qty_change = qty_change
            self.update_stock_balance(stock_entry.item_code, stock_entry.warehouse, qty_change, previous_qty_change)
            stock_entry.save(ignore_permissions=True)

    def create_stock_ledger_entry(self, item_code, warehouse, qty_change):
        """Creates a new Stock Ledger Entry."""
        if self.type == "Stock Creation":
            self.create_item_if_not_exists(item_code)

        stock_entry = frappe.new_doc("Stock Ledger Entry")
        stock_entry.update({
            "item_code": item_code,
            "warehouse": warehouse,
            "qty_change": qty_change,
            "stock_ledger": self.name
        })
        stock_entry.save(ignore_permissions=True)
        self.update_stock_balance(item_code, warehouse, qty_change)

    def handle_orphaned_entries(self, existing_entry_names, cancel, delete):
        """Handles orphaned Stock Ledger Entries."""
        for entry_name in existing_entry_names:
            stock_entry = frappe.get_doc("Stock Ledger Entry", entry_name)
            if cancel:
                stock_entry.cancel()
            elif delete:
                stock_entry.delete()

    def create_item_if_not_exists(self, item_code):
        """Creates a new Item if it doesn't exist."""
        if not frappe.db.exists("Item", item_code):
            try:
                item_details = frappe.get_doc(self.reference_type, self.reference)
                item_group = "Raw Materials" if self.reference_type == "Raw Materials Registration" else "Finished Goods"

                item = frappe.new_doc("Item")
                item.update({
                    "item_group": item_group,
                    "item_code": item_code,
                    "item_name": item_code,
                    "uom": item_details.get("uom", "Nos"),
                    "default_warehouse": item_details.get("default_warehouse")
                })
                item.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Error creating item {item_code}: {e}", "Stock Ledger")
                frappe.throw(f"Failed to create item {item_code}. Check logs for details.")

    def update_stock_balance(self, item_code, warehouse, qty_change, previous_qty_change=None):
        """Updates the stock balance for the given item and warehouse."""
        if not item_code or not warehouse:
            frappe.throw("Item Code and Warehouse are required to update stock balance.")

        # Handle Stock Adjustment: directly set stock balance to qty_change
        if self.type == "Stock Adjustment":
            new_stock_balance = qty_change
        else:
            stock_balance = frappe.db.get_value(
                "Stock Balance",
                {"item": item_code, "warehouse": warehouse},
                "qty"
            ) or 0

            if previous_qty_change is not None:
                stock_balance -= previous_qty_change

            new_stock_balance = stock_balance + qty_change

        if frappe.db.exists("Stock Balance", {"item": item_code, "warehouse": warehouse}):
            frappe.db.set_value("Stock Balance", {"item": item_code, "warehouse": warehouse}, "qty", new_stock_balance)
        else:
            stock_balance_doc = frappe.new_doc("Stock Balance")
            stock_balance_doc.update({
                "item": item_code,
                "warehouse": warehouse,
                "qty": new_stock_balance
            })
            stock_balance_doc.insert()