# Copyright (c) 2024, Harsh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Interview(Document):
	pass


@frappe.whitelist()
def update_candidate_status_client(candidate):
    interviews = frappe.get_all('Interview',
                                filters={'candidate': candidate},
                                fields=['current_round', 'outcome'])

    if not interviews:
        frappe.db.set_value('Candidate', candidate, 'status', 'Pending')
        return 'Pending'

    all_approved = True
    for interview in interviews:
        if interview.outcome == 'Rejected':
            frappe.db.set_value('Candidate', candidate, 'status', 'Rejected')
            return 'Rejected'
        elif interview.outcome != 'Approved':
            all_approved = False

    if all_approved:
        frappe.db.set_value('Candidate', candidate, 'status', 'Approved')
        return 'Approved'
    else:
        pending_rounds = [interview['current_round'] for interview in interviews if interview['outcome'] == 'Pending']
        if pending_rounds:
            frappe.db.set_value('Candidate', candidate, 'status', pending_rounds[-1])
            return pending_rounds[-1]
        else:
            last_completed_round = interviews[-1]['current_round']
            frappe.db.set_value('Candidate', candidate, 'status', last_completed_round)
            return last_completed_round
