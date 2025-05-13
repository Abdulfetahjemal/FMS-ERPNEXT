# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FactoryFloor(Document):
	pass
# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FactoryFloor(Document):
    pass

def update_factory_floor(site, items):
    """
    Creates or updates a Factory Floor entry for the given site.
    For each received item, it checks if a matching item already exists in the child table.
    If it does, it updates the measure; otherwise, it creates a new child table entry.

    Args:
        site (str): The site for the Factory Floor.
        items (list of dict): A list of dictionaries containing item details.
                              Each dictionary should have 'item' (item code), 'measure', and 'uom'.
    """
    factory_floor_doc = frappe.db.exists("Factory Floor", {"site": site})
    if factory_floor_doc:
        factory_floor = frappe.get_doc("Factory Floor", factory_floor_doc)
    else:
        factory_floor = frappe.new_doc("Factory Floor")
        factory_floor.site = site

    for item_data in items:
        item_code = item_data.get("item")
        measure = item_data.get("measure")
        uom = item_data.get("uom")

        if not item_code or not measure or not uom:
            frappe.throw("Item code, measure, and UOM are required for each item.")

        found = False
        for stored_item in factory_floor.get("stored"):
            if stored_item.item == item_code:
                stored_item.measure += measure
                found = True
                break

        if not found:
            factory_floor.append("stored", {
                "item": item_code,
                "measure": measure,
                "uom": uom
            })

    factory_floor.save()
    frappe.db.commit()

    return factory_floor
def update_factory_floor_used(site, items):
    """
    Creates or updates a Factory Floor entry for the given site.
    For each received item, it checks if a matching item already exists in the child table.
    If it does, it subtracts the measure; otherwise, it creates a new child table entry with negative value.

    Args:
        site (str): The site for the Factory Floor.
        items (list of dict): A list of dictionaries containing item details.
                              Each dictionary should have 'item' (item code), 'measure', and 'uom'.
    """
    factory_floor_doc = frappe.db.exists("Factory Floor", {"site": site})
    if factory_floor_doc:
        factory_floor = frappe.get_doc("Factory Floor", factory_floor_doc)
    else:
        factory_floor = frappe.new_doc("Factory Floor")
        factory_floor.site = site

    for item_data in items:
        item_code = item_data.get("item")
        measure = item_data.get("measure")
        uom = item_data.get("uom")

        if not item_code or not measure or not uom:
            frappe.throw("Item code, measure, and UOM are required for each item.")

        found = False
        for stored_item in factory_floor.get("stored"):
            if stored_item.item == item_code:
                stored_item.measure -= measure
                found = True
                break

        if not found:
            factory_floor.append("stored", {
                "item": item_code,
                "measure": -measure,
                "uom": uom
            })

    factory_floor.save()
    frappe.db.commit()

    return factory_floor