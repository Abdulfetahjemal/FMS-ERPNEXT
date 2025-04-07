# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe


class Client(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        address: DF.Data
        name1: DF.Data
        phone_number: DF.Phone
    # end: auto-generated types

    def after_insert(self):
        # Create a Client Balance History entry upon client creation
        frappe.get_doc({
            "doctype": "Client Balance History",
            "client": self.name,
            "date": frappe.utils.today(),
            "time": frappe.utils.now_datetime().time(),
            "previous_balance": 0.0,
            "new_balance": self.balance,
            "amount_changed": self.balance,
            "remark": "Initial balance",
            "document_type": "Client",
			"document_name": self.name,
            "doc_status": 1,
        }).insert(ignore_permissions=True)
