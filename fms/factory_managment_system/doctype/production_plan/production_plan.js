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
                    fieldname: ["estimated_p"]
                },
                callback: function(r) {
                    if (r.message) {
                        let estimated_p = r.message.estimated_p;
                        frm.set_value("estimated_p", estimated_p * frm.doc.batch);
                    }
                }
            });
        } else {
            frm.set_value("estimated_p", 0);
        }
           if (frm.doc.formula && frm.doc.batch) {
            
            frappe.call({
                method: "fms.factory_managment_system.doctype.production_plan.production_plan.get_raw_materials",
                args: {
                    formula_name: frm.doc.formula
                },
                callback: function(r) {
                    if (r.message) {
                        
                        // Build the HTML content
                        let html_content = '<table class="table table-bordered">'; // Start a table
                        html_content += '<thead><tr><th>Raw Material</th><th>Quantity</th><th>Unit</th></tr></thead>'; // Table header
                        html_content += '<tbody>';

                        r.message.forEach(item => {
                            let calculated_quantity = item.quantity;
                            if (frm.doc.batch && !isNaN(frm.doc.batch)) {
                                calculated_quantity = item.quantity * frm.doc.batch;
                            }
                            console.log(`Raw Material: ${item.raw_material}, Quantity: ${item.quantity}, Calculated Quantity: ${calculated_quantity}`);
                            html_content += `<tr><td>${item.raw_material}</td><td>${calculated_quantity}</td><td>${item.unit}</td></tr>`;
                        });

                        html_content += '</tbody></table>';

                        // Set the HTML field value
                        frm.fields_dict['formula_data'].$wrapper.html(html_content);
                    } 
                }
            });
        } else {
            // If no formula is selected, clear the HTML field
            frm.fields_dict['formula_data'].$wrapper.html('');

        }
    },
    formula: function(frm) {
        if (frm.doc.formula) {
            
            frappe.call({
                method: "fms.factory_managment_system.doctype.production_plan.production_plan.get_raw_materials",
                args: {
                    formula_name: frm.doc.formula
                },
                callback: function(r) {
                    if (r.message) {
                        
                        // Build the HTML content
                        let html_content = '<table class="table table-bordered">'; // Start a table
                        html_content += '<thead><tr><th>Raw Material</th><th>Quantity</th><th>Unit</th></tr></thead>'; // Table header
                        html_content += '<tbody>';

                        r.message.forEach(item => {
                            let calculated_quantity = item.quantity;
                            if (frm.doc.batch && !isNaN(frm.doc.batch)) {
                                calculated_quantity = item.quantity * frm.doc.batch;
                            }
                            console.log(`Raw Material: ${item.raw_material}, Quantity: ${item.quantity}, Calculated Quantity: ${calculated_quantity}`);
                            html_content += `<tr><td>${item.raw_material}</td><td>${calculated_quantity}</td><td>${item.unit}</td></tr>`;
                        });

                        html_content += '</tbody></table>';

                        // Set the HTML field value
                        frm.fields_dict['formula_data'].$wrapper.html(html_content);
                    } 
                }
            });
        } else {
            // If no formula is selected, clear the HTML field
            frm.fields_dict['formula_data'].$wrapper.html('');

        }
    },
    refresh: function(frm) {
        if (frm.doc.status === "Production Finished") {
            frm.add_custom_button(__("Create Finished Good Request"), function() {
                frappe.new_doc("Finished Good Request", {
                    production_plan: frm.doc.name, // Assuming you want to link the Production Plan
                    finished_good: frm.doc.finished_good, // Assuming you want to pre-fill the finished good
                    batch: frm.doc.batch, // Assuming you want to pre-fill the batch
                    estimated: frm.doc.estimated_p, // Assuming you want to pre-fill the estimated production
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