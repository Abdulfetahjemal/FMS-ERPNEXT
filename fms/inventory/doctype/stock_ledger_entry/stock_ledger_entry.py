# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from fms.inventory.doctype.stock_balance.stock_balance import update_item_inventory_count

class StockLedgerEntry(Document):
	def on_update(self):
		"""
		Handle the update of Stock Ledger Entry.
		"""
		enqueue(
			update_item_inventory_count,  # Function to run in the background
			item_name=self.item_code,  # Argument to pass to the function
			job_name=f"update_item_inventory_{self.item_code}", #give it a unique name
			#  The job name should be unique.  Including the item name makes it unique.
			is_async=True  # Run the job asynchronously
		)
