# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from fms.inventory.doctype.stock_balance.stock_balance import populate_stock_balance_for_item


class Item(Document):
    def after_insert(self):
        try:
            # Ensure the enqueue function is called with valid arguments
            enqueue(
                populate_stock_balance_for_item,             
                is_async=True,    # Explicitly specify that the job is asynchronous
                item_name=self.name
            )
        except Exception as e:
            # Log the exception for debugging purposes
            frappe.log_error(message=str(e), title="Error in Item.after_insert")
        