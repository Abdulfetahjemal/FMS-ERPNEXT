# Copyright (c) 2025, birukassefa123@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.password import update_password
from frappe.utils.background_jobs import enqueue


class EmployeeRegistration(Document):
    def validate(self):
        """
        Validate the inputs before submission.
        """
        if not self.email:
            frappe.throw("Email is a required field.")
        if not self.password:
            frappe.throw("Password is a required field.")
        if not self.first_name:
            frappe.throw("First Name is a required field.")
        if not self.title:
            frappe.throw("Title is a required field.")
        if not self.phone_number:
            frappe.throw("Phone Number is a required field.")
        if not self.site:
            frappe.throw("Site is a required field.")

    def on_submit(self):
        """
        Enqueue the creation of a User and Employee record when the
        Employee Registration document is submitted.
        """
        enqueue(
            method=self.create_user_and_employee,
            queue="default",
            timeout=300,
            job_name=f"Create User and Employee for {self.email}",
            email=self.email,
            first_name=self.first_name,
            title=self.title,
            password=self.password,
            phone_number=self.phone_number,
            site=self.site,
        )
        frappe.msgprint(f"User and Employee creation for {self.email} has been enqueued.")

    def create_user_and_employee(self, email, first_name, title, password, phone_number, site):
        """
        Create a User if it doesn't exist and then create an Employee.
        """
        # Check if a User with this email already exists
        if not frappe.db.exists("User", {"email": email}):
            # Create a new User
            new_user = frappe.new_doc("User")
            new_user.email = email
            new_user.first_name = first_name
            new_user.username = email  # You might want a different username generation logic
            new_user.phone = phone_number

            # Assign a role profile based on the title
            if frappe.db.exists("Role Profile", {"name": title}):
                new_user.role_profile_name = title

            new_user.save()

            # Set the password securely
            update_password(new_user.name, password)

            frappe.msgprint(f"User {email} created successfully with role profile {title}.")
        else:
            new_user = frappe.get_doc("User", {"email": email})
            frappe.msgprint(f"User {email} already exists.")

        # Check if an Employee record already exists for this user
        if not frappe.db.exists("Employee", {"employee": new_user.name}):
            # Create a new Employee
            new_employee = frappe.new_doc("Employee")
            new_employee.employee = new_user.name
            new_employee.title = title
            new_employee.site = site
            new_employee.phone_number = phone_number
            new_employee.save()
            frappe.msgprint(f"Employee record created for user {email}.")
        else:
            frappe.msgprint(f"Employee record already exists for user {email}.")