# Copyright (c) 2024, Harsh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Interview(Document):
	pass


@frappe.whitelist()
def update_candidate_status_client(candidate):
    rounds = ["Screening", "Aptitude", "Technical", "HR"]
    
    # Initialize flags and variables
    all_hired = True
    any_no_hire = False
    any_on_hold = False
    most_recent_round = None

    for round_name in rounds:
        outcome = frappe.db.get_value('Interview', {'candidate': candidate, 'current_round': round_name}, 'outcome')

        if outcome:
            most_recent_round = round_name
            if outcome == "No Hire":
                any_no_hire = True
                break
            elif outcome in ["Weak Hire", "Hire", "Strong Hire"]:
                continue
            elif outcome == "On Hold":
                any_on_hold = True
                break
            else:
                all_hired = False
                break   
        else:
            all_hired = False

    # Determine the candidate status based on the outcomes
    if any_no_hire:
        frappe.db.set_value('Candidate', candidate, 'status', 'Not Hired')
        return 'Not Hired'
    elif any_on_hold:
        frappe.db.set_value('Candidate', candidate, 'status', 'On Hold')
        return 'On Hold'
    elif all_hired and most_recent_round == rounds[-1]:
        frappe.db.set_value('Candidate', candidate, 'status', 'Hired')
        return 'Hired'
    elif most_recent_round:
        frappe.db.set_value('Candidate', candidate, 'status', most_recent_round + ' Round')
        return most_recent_round + ' Round'
    else:
        frappe.db.set_value('Candidate', candidate, 'status', 'Pending')
        return 'Pending'

    

@frappe.whitelist()
def create_interview_reschedule(interview_id, preferred_date, preferred_time):    
    interview_reschedule = frappe.get_doc({
        'doctype': 'Interview Reschedule',
        'interview': interview_id,
        'preferred_date': preferred_date,
        'preferred_time': preferred_time
    })
    interview_reschedule.insert()
    
    return interview_reschedule.name


