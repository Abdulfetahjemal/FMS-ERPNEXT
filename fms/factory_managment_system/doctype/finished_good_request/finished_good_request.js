// Copyright (c) 2025, birukassefa123@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Finished Good Request", {
	    onload: function (frm) {

        frm.set_query("item", "used", function(doc) {
            return {
                filters: {
                    "item_group": "Raw Materials"
                }
            };
        });
    },   
});
