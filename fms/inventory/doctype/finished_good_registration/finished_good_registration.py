# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinishedGoodRegistration(Document):
	def validate(self):
		"""
		Validates that the Finished Good name doesn't conflict with an existing Item name,
		and that the Item Initial Data table doesn't have duplicate warehouses.
		"""
		self.validate_name_not_item_name()
		self.validate_duplicate_warehouses()

	def validate_name_not_item_name(self):
		"""
		Validates that the Finished Good name doesn't match an existing Item name.
		"""
		if frappe.db.exists("Item", {"item_name": self.name1}):  # Corrected field name
			frappe.throw(
				f"Finished Good name '{self.name1}' already exists as an Item name. Please choose a different name.",
				title="Name Conflict",  # Add a title for the error dialog
			)

	def validate_duplicate_warehouses(self):
		"""
		Validates that the Item Initial Data table doesn't have duplicate warehouses.
		"""
		warehouses = [d.warehouse for d in self.stock_info]  # Get warehouse names
		if len(warehouses) != len(set(warehouses)):
			frappe.throw(
				"Duplicate warehouses found in Warehouse table. Please ensure each warehouse is listed only once.",
				title="Duplicate Warehouse",  # Add a title
			)

	def on_submit(self):
		"""
		Creates a Stock Ledger entry for the initial stock of the finished good.
		"""
		try:
			# 1. Create a Stock Ledger document
			stock_ledger = frappe.new_doc("Stock Ledger")
			stock_ledger.reference_type = self.doctype  # Set the reference type
			stock_ledger.reference = self.name          # and reference name
			stock_ledger.remarks = f"Initial stock for Finished Good: {self.name}"  # Add a descriptive remark.
			stock_ledger.type = "Stock Creation"              # Set the stock ledger type
			# 2. Append Stock Ledger Items directly to the Stock Ledger's child table
			for data in self.stock_info:
				stock_ledger.append("item_info", {
					"item": self.name,                  # Use the correct item field from stock_info
					"quantity": data.qty,              # Set the quantity
					"warehouse": data.warehouse,
					"uom":self.units        
				})

			# 3. Save the Stock Ledger document
			stock_ledger.save()
			frappe.msgprint(f"Stock Ledger {stock_ledger.name} created for initial quantities.")

		except Exception as e:
			# Handle errors during Stock Ledger or Entry creation
			frappe.log_error(f"Error creating Stock Ledger: {e}", "Finished Good")
			frappe.msgprint("Error creating Stock Ledger. Check logs.")
			raise  # Re-raise to prevent the Finished Good from being submitted without proper stock tracking
