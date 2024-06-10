# Copyright (c) 2024, Harsh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Interview(Document):
	pass


@frappe.whitelist()
def update_candidate_status_client(candidate):
    rounds = ["Aptitude", "Screening", "Technical", "HR"]
    
    # Initialize flags and variables
    all_approved = True
    any_rejected = False
    most_recent_approved_round = None
    rounds_checked = 0

    # Iterate through each round and check the outcome
    for round_name in rounds:
        outcome = frappe.db.get_value('Interview', {'candidate': candidate, 'current_round': round_name}, 'outcome')
        
        if outcome:
            rounds_checked += 1
            if outcome == "Rejected":
                any_rejected = True
                break
            elif outcome == "Approved":
                most_recent_approved_round = round_name
            else:
                all_approved = False
        else:
            all_approved = False

    # Determine the candidate status based on the outcomes
    if any_rejected:
        frappe.db.set_value('Candidate', candidate, 'status', 'Rejected')
        return 'Rejected'
    elif all_approved and rounds_checked == len(rounds):
        frappe.db.set_value('Candidate', candidate, 'status', 'Approved')
        return 'Approved'
    elif most_recent_approved_round:
        frappe.db.set_value('Candidate', candidate, 'status', most_recent_approved_round)
        return most_recent_approved_round
    else:
        frappe.db.set_value('Candidate', candidate, 'status', 'Pending')
        return 'Pending'