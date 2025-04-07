# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint

class FinishedGoodFormula(Document):
    def validate(self):
        self.ensure_single_active_formula()

    def ensure_single_active_formula(self):
        # If this formula is being marked as active, check for others
        if cint(self.active) == 1 and self.finished_good:
            # Check if another active formula exists for the same finished good
            # Exclude the current document ('self.name') from the check
            other_active_formula_exists = frappe.db.exists(
                "Finished Good Formula",
                {
                    "finished_good": self.finished_good,
                    "active": 1,
                    "name": ["!=", self.name] # Important: Exclude the current record
                }
            )

            if other_active_formula_exists:
                # If another active formula is found, raise an error
                frappe.throw(
                    f"Another active formula already exists for Finished Good: <strong>{self.finished_good}</strong>. Please deactivate the other formula first.",
                    title="Multiple Active Formulas Not Allowed"
                )

