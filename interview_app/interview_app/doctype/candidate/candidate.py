# Copyright (c) 2024, Harsh and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
import os
from interview_app.interview_app.resume_processing.extract2 import ExtractTextInfoFromPDF
from interview_app.interview_app.doctype.interview.gpt import GenerateQuestion
import json

class Candidate(Document):
	pass


@frappe.whitelist()
def fetch_candidate_interviews(candidate_id):
    interviews = frappe.get_all('Interview', filters={'candidate': candidate_id}, fields=[
                                'current_round', 'outcome', 'interviewer', 'date'],
                                order_by='date desc')
    return interviews

# GENERATE SCREENING ROUND QUESTIONS

@frappe.whitelist()
def generate_questions(docname):
    candidate = frappe.get_doc("Candidate", docname)

    if not candidate.resume:
        frappe.throw("Please upload a resume file first.")

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
        question_doc.current_round = "Screening"
        question_doc.save()
        
    candidate_doc = frappe.get_doc('Candidate', docname)
    candidate_doc.resume_summary = response['summary']
    candidate_doc.save()
    frappe.publish_realtime(event="msgprint", message="All questions have been generated.", user=frappe.session.user)
    return "Questions generated successfully"

# @frappe.whitelist()
# def get_feedback_skills(candidate):
#     interview_doc = frappe.get_doc('Interview', {'candidate': candidate, 'current_round': 'Screening'})
#     feedback = interview_doc.feedback
#     print("feedback for the screening round is:", feedback)
#     skills_feedback = GenerateQuestion()
#     skills = skills_feedback.get_feedback_skills(feedback=feedback) 
#     # technologies = skills.split(', ')
#     print(type(skills))
#     return skills
    

# GENERATE TECHNICAL QUESTION

@frappe.whitelist()
def generate_coding_question(candidate):
    try:
        interview_doc = frappe.get_doc('Interview', {'candidate': candidate, 'current_round': 'Screening'})
        feedback = interview_doc.feedback
        generate_coding_question_instance = GenerateQuestion()
        questions = generate_coding_question_instance.generate_coding_questions(feedback=feedback)
        print(type(questions))
        
        for question in questions:
            print(question)
            question_doc = frappe.new_doc('Question')
            question_doc.candidate = candidate
            question_doc.problem_type = question.get('problem_type', '')  # Ensure keys are correct
            question_doc.questions = question.get('problem', '')           # Ensure keys are correct
            question_doc.coding_question = question.get('boilerplate', '')# Ensure keys are correct
            question_doc.technology = ', '.join(question.get('technology', []))  # Ensure keys are correct
            question_doc.current_round = "Technical"  # Assuming `frm` is not defined in backend code
            question_doc.save()

        return {"status": "success", "message": f"{len(questions)} questions generated and saved successfully."}
    
    except Exception as e:
        frappe.log_error(f"Error in generate_coding_question: {e}")
        return {"status": "error", "message": str(e)}