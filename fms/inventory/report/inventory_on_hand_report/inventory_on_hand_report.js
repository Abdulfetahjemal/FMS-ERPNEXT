// Copyright (c) 2025, birukassefa123@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Inventory on Hand Report"] = {
    "filters": [
        {
            "fieldname":"warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouses"
        },
        {
            "fieldname":"item_code",
            "label": __("Item Code"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname":"site",
            "label": __("Site"),
            "fieldtype": "Link",
            "options": "Site",
            "default": frappe.defaults.get_default("Site")
        }
    ],
    "formatter": function (value, row, column, data, default_formatter) {
        if (column.fieldname == "qty") {
            value = formatNumber(value, column, data);
        }
        return default_formatter(value, row, column, data);
    },
    "onload": function(report) {
        report.wrapper.on('click', '.btn-primary', function() {
            report.refresh();
        });
    },
    "get_data": function(filters) {
        var data = frappe.db.get_list({
            doctype: "Stock Balance",
            fields: ["item", "warehouse", "qty"],
            filters: filters
        });
        return data;
    },
    "get_columns": function() {
        return [
            {
                "fieldname":"item",
                "label": __("Item"),
                "fieldtype": "Link",
                "options": "Item",
                "width": 200
            },
            {
                "fieldname":"warehouse",
                "label": __("Warehouse"),
                "fieldtype": "Link",
                "options": "Warehouse",
                "width": 200
            },
            {
                "fieldname":"qty",
                "label": __("Quantity"),
                "fieldtype": "Float",
                "width": 120
            }
        ];
    }
};
