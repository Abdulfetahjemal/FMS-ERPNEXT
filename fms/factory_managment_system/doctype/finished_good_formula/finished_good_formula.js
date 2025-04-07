// Copyright (c) 2025, birukassefa123@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Finished Good Formula', {
    refresh(frm) {
        // Apply the filter when the form loads or refreshes
        frm.set_query("finished_good", function(doc) {
           return {
               filters: {
                   // Filter items where the item_group field is 'Finished Good'
                   // IMPORTANT: Adjust "Finished Good" if your Item Group name differs.
                   item_group: "Finished Goods"
               }
           };
       });
        apply_raw_material_filter(frm);
    },
    // Optional: Re-apply if finished_good changes, in case it affects filtering needs
    // finished_good(frm) {
    //  apply_raw_material_filter(frm);
    // }
});

// Apply the filter when a new row is added to the child table
frappe.ui.form.on('Raw Materials Child', {
    // Trigger when a new row is added to the 'raw_materials' table
    raw_materials_add(frm, cdt, cdn) {
        apply_raw_material_filter(frm, cdt, cdn);
    }
});


// Function to set the query filter
function apply_raw_material_filter(frm, cdt, cdn) {
    // Set the query for the 'raw_material' field within the 'raw_materials' child table grid
    // Note: "raw_materials" is the fieldname of the child table in the parent DocType (Finished Good Formula)
    frm.set_query("raw_material", "raw_materials", function(doc, child_cdt, child_cdn) {

        console.log("Applying filter for Raw Material Item Group"); // Debug log

        return {
            filters: {

                item_group: "Raw Materials"
            }
        };
    });

}