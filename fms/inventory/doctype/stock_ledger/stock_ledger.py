# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockLedger(Document):
	def on_submit(self):
		"""
		On Stock Ledger submit, update or create Stock Ledger Entries.
		"""
		self.update_or_create_stock_ledger_entries()

	def on_cancel(self):
		"""
		On Stock Ledger cancel, cancel the linked Stock Ledger Entries if they exist.
		"""
		self.update_or_create_stock_ledger_entries(cancel=True)

	def on_trash(self):
		"""
		On Stock Ledger trash, trash the linked Stock Ledger Entries if they exist.
		"""
		self.update_or_create_stock_ledger_entries(delete=True)
	def on_update(self):
		frappe.msgprint("Stock Ledger Entry has been saved successfully.")
		"""
		On Stock Ledger save, update the stock Ledger Entries.
		"""
		self.update_or_create_stock_ledger_entries()
	def after_insert(self):
		frappe.msgprint("Stock Ledger Entry has been saved successfully.")
		"""
		On Stock Ledger save, update the stock Ledger Entries.
		"""
		self.update_or_create_stock_ledger_entries()
	def update_or_create_stock_ledger_entries(self, cancel=False, delete=False):
		"""
		Updates existing Stock Ledger Entries or creates new ones based on the Stock Ledger.
		Handles cancel and delete scenarios as well.
		"""
		try:
			# 1. Get existing Stock Ledger Entries linked to this Stock Ledger
			existing_entries = frappe.get_all(
				"Stock Ledger Entry",
				filters={"stock_ledger": self.name},
				fields=["name"]
			)
			existing_entry_names = [entry["name"] for entry in existing_entries]  # List of existing SLE names

			# 2. Iterate through the items in the Stock Ledger's item_info table
			for item_data in self.item_info:
				item_code = item_data.item
				warehouse = item_data.warehouse
				qty_change = item_data.quantity

				# 3. Attempt to find an existing Stock Ledger Entry with this key
				matching_entry_name = frappe.db.get_value(
					"Stock Ledger Entry",
					{"stock_ledger": self.name, "item_code": item_code, "warehouse": warehouse}
				)

				if matching_entry_name:
					self.update_stock_ledger_entry(matching_entry_name, qty_change, cancel, delete)
					if matching_entry_name in existing_entry_names:
							existing_entry_names.remove(matching_entry_name)
				else:
					if not cancel and not delete:
						self.create_stock_ledger_entry(item_code, warehouse, qty_change)

			# 6.  Handle any remaining existing Stock Ledger Entries that were not updated.
			#     This means they are no longer in the Stock Ledger's item_info and should be cancelled or deleted.
			self.handle_orphaned_entries(existing_entry_names, cancel, delete)

		except Exception as e:
			# Handle errors during Stock Ledger Entry update/creation
			frappe.log_error(f"Error updating/creating Stock Ledger Entries: {e}", "Stock Ledger")
			frappe.msgprint("Error updating/creating Stock Ledger Entries. Check logs.")
			raise  # Re-raise to prevent the Stock Ledger operation from completing



	def update_stock_ledger_entry(self, entry_name, qty_change, cancel=False, delete=False):
		"""Updates an existing Stock Ledger Entry."""
		stock_entry = frappe.get_doc("Stock Ledger Entry", entry_name)
		if cancel:
			stock_entry.cancel()
			frappe.msgprint(f"Stock Ledger Entry {stock_entry.name} cancelled.")
		elif delete:
			stock_entry.delete()
			frappe.msgprint(f"Stock Ledger Entry {stock_entry.name} deleted.")
		else:
			stock_entry.qty_change = qty_change
			# stock_entry.actual_qty =  #  You'll need logic to calculate this.
			# stock_entry.valuation_rate =  #  You'll need logic for this.
			stock_entry.save(ignore_permissions=True)
			frappe.msgprint(f"Stock Ledger Entry {stock_entry.name} updated.")

	def create_stock_ledger_entry(self, item_code, warehouse, qty_change):
		"""Creates a new Stock Ledger Entry."""

		if self.type == "Stock Creation":
			self.create_item_if_not_exists(item_code)

		stock_entry = frappe.new_doc("Stock Ledger Entry")
		stock_entry.item_code = item_code
		stock_entry.warehouse = warehouse
		stock_entry.qty_change = qty_change
		stock_entry.stock_ledger = self.name  # Link to the Stock Ledger
		stock_entry.save(ignore_permissions=True)
		frappe.msgprint(f"Stock Ledger Entry {stock_entry.name} created.")

	def handle_orphaned_entries(self, existing_entry_names, cancel, delete):
		"""Handles any remaining existing Stock Ledger Entries that were not updated."""
		for entry_name in existing_entry_names:
			stock_entry = frappe.get_doc("Stock Ledger Entry", entry_name)
			if cancel:
				stock_entry.cancel()
				frappe.msgprint(f"Stock Ledger Entry {stock_entry.name} cancelled (orphaned).")
			elif delete:
				stock_entry.delete()
				frappe.msgprint(f"Stock Ledger Entry {stock_entry.name} deleted (orphaned).")

	def create_item_if_not_exists(self, item_code):
		"""Creates a new Item if it doesn't exist."""
		if not frappe.db.exists("Item", item_code):
			# Get the Finished Good document to access its fields
			docname = self.reference  # Assuming self.reference holds the Finished Good name
			item_details = frappe.get_doc(self.reference_type, docname)
			# 5.2 Create the Item if it doesn't exist
			item = frappe.new_doc("Item")
			if self.reference_type == "Finished Good Registration":
				item.item_group = "Finished Goods"
				item.item_code = item_code
				item.item_name = item_code  # You might want a separate name field
				item.uom = item_details.uom  # Use UOM from Finished Good.
				item.default_warehouse = item_details.default_warehouse #set the warehouse. <-----
				item.save(ignore_permissions=True)
			elif self.reference_type == "Raw Materials Registration":
				item.item_group = "Finished Goods"
				item.item_code = item_code
				item.item_name = item_code  # You might want a separate name field
				item.uom = item_details.uom  # Use UOM from Raw Matrials.
				item.default_warehouse = item_details.default_warehouse #set the warehouse. <-----
				item.save(ignore_permissions=True)
			frappe.msgprint(f"Item {item_code} created.")
