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
    

# GENERATE TECHNICAL QUESTION

@frappe.whitelist()
def generate_coding_question(candidate, problem_type):
    try:
        interview_doc = frappe.get_doc('Interview', {'candidate': candidate, 'current_round': 'Screening'})
        feedback = interview_doc.feedback
        generate_coding_question_instance = GenerateQuestion()
        question = generate_coding_question_instance.generate_coding_questions(feedback=feedback, problem_type=problem_type)
        # print(f"Question in candidate file is: {question}")
        return {
            'problem_statement': question.get('problem_statement', ''),
            'problem_code': question.get('problem_code', '')
        }
    
    except Exception as e:
        frappe.log_error(f"Error in generate_coding_question: {e}")
        return {"status": "error", "message": str(e)}
    
    
@frappe.whitelist()
def save_coding_problem(interview_id, candidate, problem_statement, problem_code):
    try:
        interview_doc = frappe.get_doc('Interview', interview_id)

        interview_doc.append('problems', {
            'candidate': candidate,
            'problem_statement': problem_statement,
            'problem_code': problem_code,
            'interviewer': frappe.session.user
        })

        # Save the document
        interview_doc.save()

        return {"status": "success", "message": "Coding problem saved successfully."}
    
    except Exception as e:
        frappe.log_error(f"Error saving coding problem: {e}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_coding_problems(interview_id):
    try:
        # Fetch the Interview document
        interview_doc = frappe.get_doc('Interview', interview_id)

        # Return the problems
        return interview_doc.problems

    except Exception as e:
        frappe.log_error(f"Error fetching coding problems: {e}")
        return {"status": "error", "message": str(e)}

    
@frappe.whitelist()
def evaluate_problems(interview_id):
    interview_doc = frappe.get_doc("Interview", interview_id)
    coding_problems = interview_doc.problems
    problem_response = {}
    for problem in coding_problems:
        key = f"{problem.problem_statement}"
        value = problem.candidate_response or "Not answered."
        problem_response[key] = value

    evaluator = GenerateQuestion()
    evaluation = evaluator.evaluate_answer(problem_response=problem_response)

    formatted_evaluation = formatter(evaluation)
    
    interview_doc.evaluated_score = formatted_evaluation
    interview_doc.is_evaluated = True
    interview_doc.save()
    return evaluation

def formatter(evaluation):
    if evaluation and isinstance(evaluation, str):
        try:
            evaluation = json.loads(evaluation)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for evaluation")
    
    if not isinstance(evaluation, dict):
        raise ValueError("Evaluation must be a dictionary")

    score = evaluation.get("Score", {})
    feedback = evaluation.get("Feedback", {})

    formatted_evaluation = []

    if 'Overall' in score:
        formatted_evaluation.append(f"Overall Score: {score['Overall']}\n")
    if 'Overall' in feedback:
        formatted_evaluation.append(f"Overall Feedback: {feedback['Overall']}\n\n")

    questions = sorted(set(score.keys()).union(feedback.keys()))

    for question in questions:
        if question != 'Overall':
            if question in score:
                formatted_evaluation.append(f"{question} Score: {score[question]}\n")
            if question in feedback:
                formatted_evaluation.append(f"{question} Feedback: {feedback[question]}\n")
            formatted_evaluation.append('\n')
    return "".join(formatted_evaluation)

