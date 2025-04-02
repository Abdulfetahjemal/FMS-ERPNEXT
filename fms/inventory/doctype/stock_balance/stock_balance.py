# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue

def create_stock_balance_entry(item_name, warehouse_name):
    """
    Helper function to create a Stock Balance entry. This is now used by the background job.
    """
    try:
        stock_balance = frappe.new_doc("Stock Balance")
        stock_balance.item = item_name
        stock_balance.warehouse = warehouse_name
        stock_balance.qty = 0
        stock_balance.insert()
        frappe.logger().info(f"Stock Balance created for {item_name} in {warehouse_name}")
    except Exception as e:
        frappe.log_error(
            f"Error creating Stock Balance for {item_name} in {warehouse_name}: {e}",
            "Stock Balance",
        )

def populate_stock_balance_for_warehouse(warehouse_name):
    """
    Background job to populate Stock Balance for a given warehouse.
    """
    try:
        frappe.logger().info(f"Starting background job for warehouse: {warehouse_name}")
        items = frappe.get_all("Item", fields=["name"])
        for item_name in items:
            if not frappe.db.exists("Stock Balance", {"item": item_name.name, "warehouse": warehouse_name}):
                create_stock_balance_entry(item_name.name, warehouse_name)
        frappe.logger().info(f"Finished background job for warehouse: {warehouse_name}")
    except Exception as e:
        frappe.log_error(f"Error in populate_stock_balance_for_warehouse: {e}", "Stock Balance")

def populate_stock_balance_for_item(item_name):
    """
    Background job to populate Stock Balance for a given Item.
    """
    try:
        frappe.logger().info(f"Starting background job for item: {item_name}")
        warehouses = frappe.get_all("Warehouses", fields=["name"])
        for warehouse_name in warehouses:
            if not frappe.db.exists("Stock Balance", {"item": item_name, "warehouse": warehouse_name.name}):
                create_stock_balance_entry(item_name, warehouse_name.name)
        frappe.logger().info(f"Finished background job for item: {item_name}")
    except Exception as e:
        frappe.log_error(f"Error in populate_stock_balance_for_item: {e}", "Stock Balance")

def update_item_inventory_count(item_name):
	"""
	Updates the Item's inventory_count to the sum of all Stock Balance quantities
	for the given item.  This function runs in the background.

	Args:
		item_name (str): The name of the Item to update.
	"""
	try:
		frappe.logger("Stock Balance", "DEBUG").info(
			f"Starting background job to update inventory count for Item: {item_name}"
		)
		# 1. Calculate the sum of quantities for the item.
		total_qty = frappe.db.get_value(
			"Stock Balance",  # DocType to query
			{"item": item_name},  # Filters: Stock Balance for this item
			"SUM(qty)",  # Field to sum
		)
		total_qty = total_qty or 0  # Ensure total_qty is 0 if None

		# 2. Get the Item document.
		item_doc = frappe.get_doc("Item", item_name)
		# 3. Update the inventory count.
		item_doc.inventory_count = total_qty
		# 4. Save the Item document.
		item_doc.save()
		frappe.logger("Stock Balance").info(
			f"Item {item_name} inventory_count updated to {total_qty} (sum of Stock Balances) in background"
		)
	except frappe.DoesNotExistError:
		# Handle the case where the Item doesn't exist.
		frappe.log_error(
			f"Item {item_name} not found while updating inventory_count in background",
			"Stock Balance",
		)
	except Exception as e:
		frappe.log_error(
			f"Error updating Item {item_name} inventory_count in background: {e}",
			"Stock Balance",
		)
		frappe.msgprint(f"Error updating Item {item_name} inventory count in the background. Check logs.")


class StockBalance(Document):
	def on_update(self):
		"""
		Updates the Item's inventory_count to the sum of all Stock Balance quantities
		for that item.
		"""
		enqueue(
			update_item_inventory_count,  # Function to run in the background
			item_name=self.item,  # Argument to pass to the function
			job_name=f"update_item_inventory_{self.item}", #give it a unique name
			#  The job name should be unique.  Including the item name makes it unique.
			is_async=True  # Run the job asynchronously
		)
		frappe.logger("Stock Balance").info(
			f"Background job enqueued to update inventory count for Item: {self.item} from Stock Balance {self.name}"
		)