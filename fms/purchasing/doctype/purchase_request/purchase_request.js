// Copyright (c) 2025, birukassefa123@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Request", {
    refresh: function(frm) {
        // No need to call apply_child_filter here, it will be called on item_type change
    },
    onload: function(frm) {
        frm.set_query("item", "details", function(doc) {
            return {
                filters: {
                    "item_group": "Raw Materials"
                }
            };
        });
    }
});

frappe.ui.form.on("Stock Child", {
    item_type: function(frm, cdt, cdn) {
        
        var child = locals[cdt][cdn];
        console.log(frm.fields_dict["details"]);
        if (child.item_type) {
            frm.fields_dict["details"].grid.fields_map['item'].get_query = null;
            frm.set_query("item", "details", function(doc) {
                return {
                    filters: {
                        "item_group": child.item_type
                    }
                };
                frm.refresh_field("details");
            });
        } else {
            frm.set_query("item", "details", function(doc) {
                return {
                    filters: {}
                };
            });
        }
    },
    item: function(frm, cdt, cdn) {
        // to fetch values of item like description and uom
        var child = locals[cdt][cdn];
        if (child.item) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Item",
                    filters: {
                        item_code: child.item
                    },
                    fieldname: ["item_name", "description", "stock_uom"]
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
                        frappe.model.set_value(cdt, cdn, "description", r.message.description);
                        frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
                        frm.refresh_field("details");
                    }
                }
            });
        }
    }
});