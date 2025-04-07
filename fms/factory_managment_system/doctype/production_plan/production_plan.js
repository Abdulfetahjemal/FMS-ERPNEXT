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
    }
});