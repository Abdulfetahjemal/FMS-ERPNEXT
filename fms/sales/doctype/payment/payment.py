# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Payment(Document):
	def on_submit(self):
	# Create a Client Balance History entry
		history_doc = frappe.new_doc("Client Balance History")
		history_doc.client = self.client
		history_doc.date = self.date
		history_doc.amount_change = self.paid
		history_doc.document_type = self.doctype
		history_doc.reference = self.name

		history_doc.insert()
	pass
