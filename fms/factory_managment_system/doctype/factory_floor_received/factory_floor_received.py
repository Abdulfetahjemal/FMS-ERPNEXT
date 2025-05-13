# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from fms.factory_managment_system.doctype.factory_floor.factory_floor import update_factory_floor


class FactoryFloorReceived(Document):
    def on_submit(self):
        items = []
        for item in self.received:
            items.append({
                "item": item.item,
                "measure": item.measure,
                "uom": item.uom
            })
        update_factory_floor(self.site, items)
