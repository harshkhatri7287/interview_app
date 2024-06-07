# Copyright (c) 2024, Harsh and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document


class Candidate(Document):
	pass


@frappe.whitelist()
def fetch_candidate_interviews(candidate_id):
    interviews = frappe.get_all('Interview', filters={'candidate': candidate_id}, fields=['current_round', 'outcome', 'interviewer', 'date'])
    return interviews


@frappe.whitelist()
def get_interview_rounds(candidate):
    interviews = frappe.get_all('Interview',
                                filters={'candidate': candidate},
                                fields=['current_round'])

    completed_rounds = [interview.current_round for interview in interviews]
    return {'completed_rounds': completed_rounds}


# @frappe.whitelist()
# def update_candidate_status(doc, method):
#     candidate = doc.candidate
#     interviews = frappe.get_all('Interview',
#                                 filters={'candidate': candidate},
#                                 fields=['current_round', 'outcome'])

#     if not interviews:
#         frappe.db.set_value('Candidate', candidate, 'status', 'Pending')
#         return

#     all_approved = True
#     for interview in interviews:
#         if interview.outcome == 'Rejected':
#             frappe.db.set_value('Candidate', candidate, 'status', 'Rejected')
#             return
#         elif interview.outcome != 'Approved':
#             all_approved = False

#     if all_approved:
#         frappe.db.set_value('Candidate', candidate, 'status', 'Approved')
#     else:
#         pending_rounds = [interview.round_type for interview in interviews if interview.outcome == 'Pending']
#         if pending_rounds:
#             frappe.db.set_value('Candidate', candidate, 'status', pending_rounds[-1])
#         else:
#             last_completed_round = interviews[-1].round_type
#             frappe.db.set_value('Candidate', candidate, 'status', last_completed_round)
	