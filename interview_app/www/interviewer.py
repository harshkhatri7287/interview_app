import frappe
def get_context(context):
    context.interviews = frappe.get_list("Interview", fields=["name", "interviewer"])
