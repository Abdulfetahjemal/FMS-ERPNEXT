# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint

class ProductionPlan(Document):
    def validate(self):
        self.validate_active_formula()

    def validate_active_formula(self):
        if not self.finished_good:
            return

        active_formula_exists = frappe.db.exists(
            "Finished Good Formula",
            {
                "finished_good": self.finished_good,
                "active": 1
            }
        )

        if not active_formula_exists:
            frappe.throw(
                f"No active Finished Good Formula found for Finished Good: <strong>{self.finished_good}</strong>. Please create or activate a formula first.",
                title="Missing Active Formula"
            )



    def on_update(self):
        
        if self.status == "Production Approved":
            self.create_stock_out()
            self.create_factory_floor_received()


    def create_stock_out(self):
        formula = frappe.get_doc("Finished Good Formula", self.formula)
        stock_ledger = frappe.new_doc("Stock Ledger")
        stock_ledger.type = "Stock Out"
        stock_ledger.reference_type = self.doctype
        stock_ledger.reference = self.name
        stock_ledger.remarks = f"Stock out for production plan {self.name}"

        for raw_material in formula.raw_materials:
            stock_ledger.append("item_info", {
                "item": raw_material.raw_material,
                "quantity": raw_material.quantity*self.batch,
                "warehouse": frappe.get_value("Item", raw_material.raw_material, "default_warehouse"),
                "uom": raw_material.unit
            })

        stock_ledger.save()

    def create_factory_floor_received(self):
        """Creates a Factory Floor Received document upon Production Plan submission."""
        factory_floor_received = frappe.new_doc("Factory Floor Received")
        factory_floor_received.production_plan = self.name
        factory_floor_received.site_employee = self.shift_leader
        # Copy raw materials from the formula to the Factory Floor Received
        formula = frappe.get_doc("Finished Good Formula", self.formula)
        for raw_material in formula.raw_materials:
            factory_floor_received.append("received", {  
                "item": raw_material.raw_material,
                "measure": raw_material.quantity * self.batch,  # Adjust measure
                "uom": raw_material.unit
            })

        factory_floor_received.docstatus = 1  # Set the status to Draft
        factory_floor_received.save()


# --- Whitelisted function added below ---
@frappe.whitelist()
def get_active_formula(finished_good):
    """
    Retrieves the name of the active Finished Good Formula for a given Finished Good.

    :param finished_good: The name of the Finished Good.
    :return: The name (ID) of the active formula, or None if not found.
    """
    if not finished_good:
        return None

    formula_name = frappe.db.get_value(
        "Finished Good Formula",
        filters={"finished_good": finished_good, "active": 1},
        fieldname="name"
    )
    return formula_name