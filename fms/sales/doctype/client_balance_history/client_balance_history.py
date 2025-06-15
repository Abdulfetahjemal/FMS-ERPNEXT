# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe


class ClientBalanceHistory(Document):
    def before_save(self):
                
        # Update the Client's balance
        client = frappe.get_doc("Client", self.client)
        
        # Check if this is not the first Client Balance History entry
        if frappe.db.count("Client Balance History", {"client": self.client}) > 1:
            current_balance = client.balance or 0  # Get current balance, default to 0 if None
            # if self.amount_change < 0 and abs(self.amount_change) > current_balance:
            #     frappe.throw("Client does not have the balance for the sale")
            new_balance = current_balance + self.amount_change
            self.new_balance = new_balance
            client.db_set("balance", new_balance)
        client.save(ignore_permissions=True)
        pass

