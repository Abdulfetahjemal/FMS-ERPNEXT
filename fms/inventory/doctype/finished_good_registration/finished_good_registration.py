# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinishedGoodRegistration(Document):
    def validate(self):
        """
        Validates the Finished Good document before saving.
        Ensures that:
        1. The Finished Good name doesn't conflict with an existing Item name.
        2. The Item Initial Data table doesn't have duplicate warehouses.
        """
        self.validate_name_not_item_name()
        self.validate_duplicate_warehouses()

    def validate_name_not_item_name(self):
        """
        Validates that the Finished Good name doesn't match an existing Item name.
        Throws an error if a conflict is found.
        """
        # Check if an Item with the same name exists in the database
        if frappe.db.exists("Item", {"item_name": self.name1}):  # Corrected field name
            # Throw an error with a descriptive message and title
            frappe.throw(
                f"Finished Good name '{self.name1}' already exists as an Item name. Please choose a different name.",
                title="Name Conflict",  # Add a title for the error dialog
            )

    def validate_duplicate_warehouses(self):
        """
        Validates that the Item Initial Data table doesn't have duplicate warehouses.
        Throws an error if duplicate warehouses are found.
        """
        # Extract the list of warehouse names from the stock_info child table
        warehouses = [d.warehouse for d in self.stock_info]
        # Check if there are duplicates by comparing the length of the list and the set
        if len(warehouses) != len(set(warehouses)):
            # Throw an error with a descriptive message and title
            frappe.throw(
                "Duplicate warehouses found in Warehouse table. Please ensure each warehouse is listed only once.",
                title="Duplicate Warehouse",  # Add a title
            )

    def on_submit(self):
        """
        Executes when the Finished Good document is submitted.
        Creates a Stock Ledger entry for the initial stock of the finished good.
        """
        try:
            # 1. Create a new Stock Ledger document
            stock_ledger = frappe.new_doc("Stock Ledger")
            stock_ledger.reference_type = self.doctype  # Set the reference type to the current document type
            stock_ledger.reference = self.name          # Set the reference name to the current document name
            stock_ledger.remarks = f"Initial stock for Finished Good: {self.name}"  # Add a descriptive remark
            stock_ledger.type = "Stock Creation"        # Set the stock ledger type to "Stock Creation"

            # 2. Append Stock Ledger Items to the Stock Ledger's child table
            for data in self.stock_info:
                stock_ledger.append("item_info", {
                    "item": self.name,                  # Use the Finished Good name as the item
                    "quantity": data.qty,              # Set the quantity from the stock_info table
                    "warehouse": data.warehouse,       # Set the warehouse from the stock_info table
                    "uom": self.uom                  # Set the unit of measure
                })

            # 3. Save the Stock Ledger document to the database
            stock_ledger.save()
            # Notify the user that the Stock Ledger was successfully created
            frappe.msgprint(f"Stock Ledger {stock_ledger.name} created for initial quantities.")

        except Exception as e:
            # Handle any errors that occur during Stock Ledger creation
            frappe.log_error(f"Error creating Stock Ledger: {e}", "Finished Good")  # Log the error for debugging
            frappe.msgprint("Error creating Stock Ledger. Check logs.")  # Notify the user of the error
            raise  # Re-raise the exception to prevent submission without proper stock tracking
