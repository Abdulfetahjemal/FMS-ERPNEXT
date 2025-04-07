# Copyright (c) 2025, birukassefa123@gmail.com and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase
import frappe


class TestProductionPlan(FrappeTestCase):
	pass
    class TestProductionPlan(FrappeTestCase):
        def test_production_plan_stock_out(self):
            # Create a Finished Good
            finished_good = frappe.get_doc({
                "doctype": "Item",
                "item_code": "Test Finished Good",
                "item_group": "Finished Goods",
                "is_stock_item": 1,
                "uom": "Nos"
            }).insert()

            # Create a Warehouse
            warehouse = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "Test Warehouse",
                "company": "_Test Company"
            }).insert()

            # Create a Finished Good Formula
            formula = frappe.get_doc({
                "doctype": "Finished Good Formula",
                "finished_good": finished_good.name,
                "active": 1,
                "raw_materials": []
            }).insert()

            # Create a Production Plan
            production_plan = frappe.get_doc({
                "doctype": "Production Plan",
                "finished_good": finished_good.name,
                "formula": formula.name,
                "batch": "Batch1",
                "approver": frappe.session.user,
                "shift_leader": frappe.session.user,
                "remark": "Test Remark"
            }).insert()

            production_plan.submit()

            # Check if Stock Ledger is created
            stock_ledger = frappe.db.exists("Stock Ledger", {"reference_type": "Production Plan", "reference": production_plan.name})
            self.assertTrue(stock_ledger)

            # Clean up
            finished_good.delete()
            warehouse.delete()
            formula.delete()
            production_plan.cancel()