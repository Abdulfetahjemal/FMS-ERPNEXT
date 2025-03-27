# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from fms.inventory.doctype.stock_balance.stock_balance import populate_stock_balance_for_warehouse

class Warehouses(Document):
    def after_insert(self):
        # Enqueue the task with is_async explicitly set to True
        enqueue(populate_stock_balance_for_warehouse, warehouse_name=self.name, is_async=True)

    