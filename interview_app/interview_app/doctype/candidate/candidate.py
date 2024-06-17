# Copyright (c) 2024, Harsh and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
import os
from interview_app.interview_app.resume_processing.extract2 import ExtractTextInfoFromPDF
import json

class Candidate(Document):
	pass


@frappe.whitelist()
def fetch_candidate_interviews(candidate_id):
    interviews = frappe.get_all('Interview', filters={'candidate': candidate_id}, fields=[
                                'current_round', 'outcome', 'interviewer', 'date'])
    return interviews


@frappe.whitelist()
def get_interview_rounds(candidate):
    interviews = frappe.get_all('Interview',
                                filters={'candidate': candidate},
                                fields=['current_round'])

    completed_rounds = [interview.current_round for interview in interviews]
    return {'completed_rounds': completed_rounds}

@frappe.whitelist()
def generate_questions(docname):
    candidate = frappe.get_doc("Candidate", docname)

    if not candidate.resume:
        frappe.throw("Please upload a resume file first.")

    # frappe.publish_realtime(event="msgprint", message="System is generating questions...please wait...", user=frappe.session.user)

    file_url = candidate.resume
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    resume_path = frappe.get_site_path("public", file_doc.file_url.lstrip("/"))
    
    extractor = ExtractTextInfoFromPDF(resume_path=resume_path, zip_path=frappe.get_site_path(
        "public", "files", f"{candidate.name}_resume_output.zip"), role_applied=candidate.role_applied)
    
    response = extractor.get_response()
    response = json.loads(response)

    for technology, questions in response.get('questions', {}).items():
        question_doc = frappe.new_doc('Question')
        question_doc.candidate = docname
        question_doc.technology = technology
        question_doc.questions = questions
        question_doc.save()
        
    candidate_doc = frappe.get_doc('Candidate', docname)
    candidate_doc.resume_summary = response['summary']
    candidate_doc.save()
    frappe.publish_realtime(event="msgprint", message="All questions have been generated.", user=frappe.session.user)
    return "Questions generated successfully"


