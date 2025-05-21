// Copyright (c) 2025, birukassefa123@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Stock Transfer Request', {
    onload: function (frm) {
        if (!frm.doc.from_shift_manager) {
            frm.set_value('from_shift_manager', frappe.session.user);
        }
        frm.set_query("item", "transferring", function(doc) {
            return {
                filters: {
                    "item_group": "Raw Materials"
                }
            };
        });
    },   
});
