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
		self.create_factory_floor_used_entry()

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
	def create_factory_floor_used_entry(self):
			"""
			Creates a Factory Floor Used entry for the finished good request.
			"""
			try:
				factory_floor_used = frappe.new_doc("Factory Floor Used")
				production_plan_doc = frappe.get_doc("Production Plan", self.production_plan)  
				factory_floor_used.site = production_plan_doc.site  # Assuming warehouse is equivalent to site
				for item in self.used:
					factory_floor_used.append("stored", {
							"item": item.item,
							"measure": item.measure,
							"uom": item.uom
							
						})

				factory_floor_used.save()
				factory_floor_used.submit()

			except frappe.exceptions.ValidationError as e:
				frappe.log_error(f"Validation Error creating Factory Floor Used entry: {e}", "Finished Good Request")
				frappe.throw(f"Validation Error: {e}. Please check your data.")

			except Exception as e:
				frappe.log_error(f"Error creating Factory Floor Used entry: {e}", "Finished Good Request")
				frappe.throw("Failed to create Factory Floor Used entry. Check logs.")