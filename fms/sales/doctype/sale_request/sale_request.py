import frappe
from frappe.model.document import Document


class SaleRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.sales.doctype.sale_request_item.sale_request_item import SaleRequestItem
		from frappe.types import DF

		amended_from: DF.Link | None
		client: DF.Link
		name1: DF.Data | None
		phone: DF.Phone | None
		remark: DF.Data | None
		sale_request_items: DF.Table[SaleRequestItem]
		sales_office_approver: DF.Link | None
		sales_site_approver: DF.Link | None
		sales_stock_approver: DF.Link | None
		status: DF.Data | None
		total_price: DF.Float
	# end: auto-generated types

	def before_save(self):
		old_status = self.get_db_value("status")
		if self.status == "Pending Sales Approval" and self.status != old_status:
			frappe.msgprint("Sale Request is pending for sales approval.")
			self.sales_office_approver = frappe.session.user
			# Create Client Balance History
			client_balance_history = frappe.new_doc("Client Balance History")
			client_balance_history.client = self.client
			client_balance_history.amount_change = self.total_price * -1  # Or calculate the actual amount change
			client_balance_history.date = frappe.utils.today()
			client_balance_history.type = "Sale"  # Or any relevant type
			client_balance_history.document_type = "Sale Request"
			client_balance_history.reference = self.name
			client_balance_history.save()

		elif self.status == "Pending Site Approval" and self.status != old_status:
			frappe.msgprint("Sale Request is pending for site approval.")
			self.sales_site_approver = frappe.session.user

		elif self.status == "Pending Stock Approval" and self.status != old_status:
			frappe.msgprint("Sale Request is pending for stock approval.")
			self.sales_stock_approver = frappe.session.user

			# Validate sale_request_items
			if not self.sale_request_items:
				frappe.throw("Sale Request Items cannot be empty when setting status to Pending Stock Approval.")

			for item in self.sale_request_items:
				item_code = getattr(item, "item", None)
				requested_qty = getattr(item, "quantity", 0)
				warehouse = getattr(item, "warehouse", None)

				if not item_code:
					frappe.throw("Item code is missing in one of the Sale Request Items.")
				if not warehouse:
					frappe.throw(f"Warehouse is required for Item: {item_code} before setting status to Pending Stock Approval.")

				stock_balance = frappe.db.get_value(
					"Stock Balance",
					{"item": item_code, "warehouse": warehouse},
					"qty",
				)

				available_stock = stock_balance if stock_balance is not None else 0

				if requested_qty > available_stock:
					frappe.throw(
						f"Insufficient Stock for Item: {item_code} in Warehouse: {warehouse}. "
						f"Requested: {requested_qty}, Available: {available_stock}."
					)

	def on_submit(self):
		stock_ledger = frappe.new_doc("Stock Ledger")
		stock_ledger.type = "Stock Out"
		stock_ledger.reference_type = "Sale Request"
		stock_ledger.reference = self.name
		stock_ledger.remarks = f"Stock Out generated from Sale Request: {self.name}"
		# Append items directly to the Stock Ledger's child table
		for item in self.sale_request_items:
			stock_ledger.append("item_info", {
				"item": item.item,
				"quantity": item.quantity,
				"warehouse": item.warehouse
			})

		stock_ledger.insert()  # Use insert() before submit() for new documents
		
		# Get Client Balance History
		client_balance_history_name = frappe.db.get_value("Client Balance History", {"reference": self.name})
		if client_balance_history_name:
			client_balance_history = frappe.get_doc("Client Balance History", client_balance_history_name)
			client_balance_history.submit()