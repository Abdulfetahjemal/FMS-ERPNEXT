frappe.ui.form.on('Sale Request', {
    refresh: function(frm) {
        // Ensure any UI refresh logic if needed
    },
    calculate_total_price: function(frm) {
        let total_price = 0;
        if (frm.doc.sale_request_items) {
            frm.doc.sale_request_items.forEach(row => {
                if (row.calculated_price) {
                    total_price += parseFloat(row.calculated_price);
                }
            });
        }
        frm.set_value('total_price', total_price);
    }
});
frappe.ui.form.on('Sale Request', {
    setup: function(frm) {
        frm.set_query('item', 'sale_request_items', function(doc, cdt, cdn) {
            return {
                filters: {
                    'item_group': 'Finished Goods' // Replace 'Finished Goods' with your desired item group
                }
            };
        });
    }
});

frappe.ui.form.on('Sale Request Item', {
    quantity: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item) {
            frappe.db.get_value('Item', row.item, 'cost', (r) => {
                if (r && r.cost) {
                    row.calculated_price = row.quantity * r.cost;
                    frm.refresh_field('sale_request_items');
                    frm.trigger('calculate_total_price'); // Call the total price calculation
                } else {
                    row.calculated_price = 0;
                    frm.refresh_field('sale_request_items');
                    frm.trigger('calculate_total_price'); // Call the total price calculation
                }
            });
        } else {
            row.calculated_price = 0;
            frm.refresh_field('sale_request_items');
            frm.trigger('calculate_total_price'); // Call the total price calculation
        }
    },
    item: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item) {
            frappe.db.get_value('Item', row.item, 'cost', (r) => {
                if (r && r.cost) {
                    row.calculated_price = row.quantity * r.cost;
                    frm.refresh_field('sale_request_items');
                    frm.trigger('calculate_total_price'); // Call the total price calculation
                } else {
                    row.calculated_price = 0;
                    frm.refresh_field('sale_request_items');
                    frm.trigger('calculate_total_price'); // Call the total price calculation
                }
            });
        } else {
            row.calculated_price = 0;
            frm.refresh_field('sale_request_items');
            frm.trigger('calculate_total_price'); // Call the total price calculation
        }
    }
});

frappe.ui.form.on('Sale Request', {
    sale_request_items_add: function(frm, cdt, cdn) {
        var row = frm.get_doc(cdt, cdn);
        if (row.item) {
            frappe.db.get_value('Item', row.item, 'cost', (r) => {
                if (r && r.cost) {
                    row.calculated_price = row.quantity * r.cost;
                    frm.refresh_field('sale_request_items');
                    frm.trigger('calculate_total_price'); // Call the total price calculation
                } else {
                    frm.trigger('calculate_total_price');
                }
            });
        } else {
            frm.trigger('calculate_total_price'); // Call the total price calculation
        }
    },
    after_remove: function(frm) {
        frm.trigger('calculate_total_price'); // Recalculate total when a row is removed
    }
});