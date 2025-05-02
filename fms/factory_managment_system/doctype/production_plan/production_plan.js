// Copyright (c) 2025, birukassefa123@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Production Plan", {
    setup(frm) {
        // Apply the filter when the form loads or refreshes
        frm.set_query("finished_good", function(doc) {
           return {
               filters: {
                   item_group: "Finished Goods"
               }
           };
       });
       
    },
    finished_good: function(frm) {
        // Inside the finished_good: function(frm) { ... } handler:

        if (frm.doc.finished_good) {
            // Call the server-side function when finished_good changes
            frappe.call({
                // *** IMPORTANT: Replace 'YOUR_ACTUAL_APP_NAME' below ***
                // Use the real internal name of your custom Frappe app.
                method: "fms.factory_managment_system.doctype.production_plan.production_plan.get_active_formula",
                args: {
                    finished_good: frm.doc.finished_good
                },
                callback: function(r) {
                    if (r.message) {
                        // Set the formula field if an active formula is found
                        frm.set_value('formula', r.message);
                    } else {

                        frappe.show_alert({ message: __("No active formula found for the selected Finished Good."), indicator: "orange" });
                        frm.set_value('formula', ''); // Clear if no active formula found
                    }
                }
            });
        } else {
            frm.set_value('formula', ''); // Clear if finished good is cleared
        }
    },
    batch: function(frm) {
        if (frm.doc.formula && frm.doc.batch) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Finished Good Formula",
                    filters: {name: frm.doc.formula},
                    fieldname: ["estimated_production"]
                },
                callback: function(r) {
                    if (r.message) {
                        let estimated_production = r.message.estimated_production;
                        frm.set_value("estimated_production", estimated_production * frm.doc.batch);
                    }
                }
            });
        } else {
            frm.set_value("estimated_production", 0);
        }
    },
    formula: function(frm) {
         if (frm.doc.formula && frm.doc.batch) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Finished Good Formula",
                    filters: {name: frm.doc.formula},
                    fieldname: ["estimated_production"]
                },
                callback: function(r) {
                    if (r.message) {
                        let estimated_production = r.message.estimated_production;
                        frm.set_value("estimated_production", estimated_production * frm.doc.batch);
                    }
                }
            });
        } else {
            frm.set_value("estimated_production", 0);
        }
    },
    refresh: function(frm) {
        if (frm.doc.status === "Production Finished") {
            frm.add_custom_button(__("Create Finished Good Request"), function() {
                frappe.new_doc("Finished Good Request", {
                    production_plan: frm.doc.name, // Assuming you want to link the Production Plan
                    finished_good: frm.doc.finished_good, // Assuming you want to pre-fill the finished good
                    batch: frm.doc.batch, // Assuming you want to pre-fill the batch
                    estimated: frm.doc.estimated_production, // Assuming you want to pre-fill the estimated production
                    // You can pre-fill other fields as needed
                });
            });
            frm.add_custom_button(__("Create Work Stock Transfer Request"), function() {
                frappe.new_doc("Work Stock Transfer Request", {
                    production_plan: frm.doc.name,
                    // You can pre-fill other fields as needed
                });
                // frappe.call({
                //     method: "frappe.client.get_list",
                //     args: {
                //         doctype: "Raw Materials Child",
                //         filters: {
                //             parenttype: "Finished Good Formula",
                //             parent: frm.doc.formula
                //         },
                //         fields: ["raw_material"]
                //     },
                //     callback: function(r) {
                //         if (r.message) {
                //             r.message.forEach(item => {
                //                 frappe.model.add_child(cur_frm.doc, "Work Stock Transfer Request Item", "items");
                //                 cur_frm.doc.items[cur_frm.doc.items.length - 1].raw_material = item.raw_material;
                //                 cur_frm.doc.items[cur_frm.doc.items.length - 1].quantity = 0;
                //             });
                //             refresh_field("items");
                //         }
                //     }
                // });
            });
        }
    }
});