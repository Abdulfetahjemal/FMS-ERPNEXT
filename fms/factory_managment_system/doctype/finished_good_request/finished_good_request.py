# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinishedGoodRequest(Document):
	def on_submit(self):
		"""
		Create a Stock In entry in the Stock Ledger upon submission of a Finished Good Request.
		"""
		self.create_stock_ledger_entry()

	def create_stock_ledger_entry(self):
		"""
		Creates a Stock Ledger entry for the finished good request.
		"""
		try:
			stock_ledger = frappe.new_doc("Stock Ledger")
			stock_ledger.type = "Stock In"
			stock_ledger.reference_type = self.doctype
			stock_ledger.reference = self.name
			stock_ledger.remarks = f"Stock In for Finished Good Request: {self.name}"
			stock_ledger.append("item_info", {
					"item": self.finished_good,
					"quantity": self.quantity,
					"warehouse": self.warehouse,
					"uom": frappe.db.get_value("Item", self.finished_good, "uom"),
				})

			stock_ledger.save()

		except frappe.exceptions.ValidationError as e:
			frappe.log_error(f"Validation Error creating Stock Ledger entry: {e}", "Finished Good Request")
			frappe.throw(f"Validation Error: {e}. Please check your data.")

		except Exception as e:
			frappe.log_error(f"Error creating Stock Ledger entry: {e}", "Finished Good Request")
			frappe.throw("Failed to create Stock Ledger entry. Check logs.")
