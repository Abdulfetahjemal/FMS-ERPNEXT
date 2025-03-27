import frappe

def execute():
    item_groups_data = [
        {"group_name": "Raw Materials", "parent_group": None},
        {"group_name": "Finished Goods", "parent_group": None},
        {"group_name": "Packaging", "parent_group": "Raw Materials"}
    ]

    for group_data in item_groups_data:
        group_name = group_data["group_name"]
        parent_group = group_data["parent_group"]

        if not frappe.db.exists("Item Groups", {"group_name": group_name}):
            item_group = frappe.new_doc("Item Groups")
            item_group.group_name = group_name
            if parent_group:
                if frappe.db.exists("Item Groups", {"group_name":parent_group}):
                    item_group.parent_group = parent_group
                else:
                    frappe.msgprint(f"Parent Group {parent_group} does not exist for {group_name}")
            item_group.insert()
            frappe.msgprint(f"Item Group {group_name} created.")
        else:
            frappe.msgprint(f"Item Group {group_name} already exists.")

if __name__ == "__main__":
    execute()