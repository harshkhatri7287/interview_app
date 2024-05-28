# Copyright (c) 2024, Harsh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Question(Document):
    pass


@frappe.whitelist()
def get_questions(candidate):
    question_docs = frappe.get_list('Question', filters={'candidate': candidate}, fields=['name', 'questions'])
    return question_docs
