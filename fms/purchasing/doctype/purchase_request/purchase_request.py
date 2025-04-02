# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PurchaseRequest(Document):
    def on_submit(self):
        if not self._validate_details():
            return

        stock_ledger = self._create_stock_ledger()

        try:
            stock_ledger.save()
        except frappe.ValidationError as e:
            self._log_and_notify_error(f"Validation error while creating Stock Ledger: {e}", "Stock Ledger Validation Error")
        except Exception as e:
            self._log_and_notify_error(f"Unexpected error while creating Stock Ledger: {e}", "Stock Ledger Creation Error")

    def _validate_details(self):
        """Validate if the Purchase Request has valid details."""
        if not self.details:
            frappe.log_error(f"Purchase Request {self.name} has no details to process.", title="Empty Purchase Request Details")
            frappe.msgprint(f"No items found in Purchase Request {self.name}. Stock Ledger creation skipped.", title="No Items Found")
            return False

        for item in self.details:
            if not all([item.item, item.quantity, item.uom, item.warehouse]):
                frappe.log_error(f"Invalid item details in Purchase Request {self.name}: {item}", title="Invalid Item Details")
        return True

    def _create_stock_ledger(self):
        """Create and populate a Stock Ledger document."""
        stock_ledger = frappe.new_doc("Stock Ledger")
        stock_ledger.type = "Stock In"
        stock_ledger.reference_type = "Purchase Request"
        stock_ledger.reference = self.name
        stock_ledger.remarks = f"Stock In generated from Purchase Request: {self.name}"

        for item in self.details:
            if all([item.item, item.quantity, item.uom, item.warehouse]):
                stock_ledger.append("item_info", {
                    "item": item.item,
                    "quantity": item.quantity,
                    "uom": item.uom,
                    "warehouse": item.warehouse
                })
        return stock_ledger

    def _log_and_notify_error(self, message, title):
        """Log an error and notify the user."""
        frappe.log_error(f"Purchase Request {self.name}: {message}", title=title)
        frappe.msgprint(f"{message}. Check error log for details.", title=title)
