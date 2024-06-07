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

    # Inform the user that the system is generating questions
    frappe.publish_realtime(event="msgprint", message="System is generating questions...", user=frappe.session.user)

    # Get the file path of the uploaded resume
    file_url = candidate.resume
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    resume_path = frappe.get_site_path("public", file_doc.file_url.lstrip("/"))
    
    # Create an instance of ExtractTextInfoFromPDF
    extractor = ExtractTextInfoFromPDF(resume_path=resume_path, zip_path=frappe.get_site_path(
        "public", "files", f"{candidate.name}_resume_output.zip"))
    
    # Get the response from the extractor
    response = extractor.get_response()
    response = json.loads(response)

    for technology, questions in response['questions'].items():
        for question_text in questions:
            # Create and save the question document
            question_doc = frappe.new_doc('Question')
            question_doc.candidate = docname
            question_doc.technology = technology
            question_doc.questions = question_text
            question_doc.save()

    # Notify user of completion
    frappe.publish_realtime(event="msgprint", message="All questions have been generated.", user=frappe.session.user)

    return "Questions generated successfully"


