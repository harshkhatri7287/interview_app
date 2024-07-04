from frappe import _

def get_data():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Define workspaces for HR and Interviewers
    hr_workspace = {
        "module_name": "HR",
        "category": "Modules",
        "label": _("HR"),
        "icon": "octicon octicon-organization",
        "type": "module",
        "standard": 1
    }

    interviewer_workspace = {
        "module_name": "Interviewer",
        "category": "Modules",
        "label": _("Interviewer"),
        "icon": "octicon octicon-person",
        "type": "module",
        "standard": 1,
        "shortcuts": [
            {
                "label": _("Interviewers"),
                "link": "List/Interviewer",
                "type": "list",
                "standard": 1
            },
            {
                "label": _("Candidates"),
                "link": "List/Candidate",
                "type": "list",
                "standard": 1
            }
        ]
    }

    # Initialize the workspaces to display
    workspaces_to_display = []

    # Show HR workspace if the user has HR role
    if "HR" in roles:
        workspaces_to_display.append(hr_workspace)

    # Show Interviewer workspace if the user has Interviewer role
    if "Interviewer" in roles:
        workspaces_to_display.append(interviewer_workspace)

    return workspaces_to_display

