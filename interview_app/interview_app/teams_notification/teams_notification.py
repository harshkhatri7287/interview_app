import requests
import json
import frappe
from frappe import _
from frappe.utils.response import build_response


def send_teams_notification(card_payload):
    keys = frappe.get_doc('Private Keys')
    url = keys.teams_webhook_url
    print(url)
    print(f"The URL is: {url}")
    headers = {
        'Content-Type': 'application/json'
    }    
    teams_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": json.loads(card_payload)
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(teams_payload))
    if response.status_code == 200:
        frappe.msgprint("Notification sent to Teams successfully!")
    else:
        frappe.msgprint(f"Failed to send notification: {response.status_code}, {response.text}")


def notify_interview_scheduled(doc, method):
    interviewer_full_name = frappe.db.get_value('User', doc.interviewer, 'full_name')
    candidate_full_name = frappe.db.get_value('Candidate', doc.candidate, 'full_name')
    
    card_payload = {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": f"**@Interviewers** , A **{doc.current_round}** interview round (**{doc.name}**) has been scheduled.",
                "size": "medium",
                "wrap" : True,
            },
            {
                "type": "TextBlock",
                "text": f"_Interviewer_ : **{interviewer_full_name}**",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": f"_Candidate Name_ : **{candidate_full_name}**",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": f"_Interview Date_ : **{doc.date}**",
                "wrap": True
            },
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Interview Page",
                "url": f"http://localhost:8000/app/interview/{doc.name}"
            },
            {
                "type": "Action.OpenUrl",
                "title": "Reschedule Request",
                "url": f"http://localhost:8000/api/method/interview_app.interview_app.teams_notification.teams_notification.handle_reschedule_request?doc_name={doc.name}"
            },
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3"
    }
    card_data = json.dumps(card_payload)
    send_teams_notification(card_data)


# Interview outcome updated message   
def notify_interview_verdict_submitted(doc, method):
    print("This function is running!")
    if (doc.get_doc_before_save()) and (doc.has_value_changed("outcome")):
        interviewer_full_name = frappe.db.get_value('User', doc.interviewer, 'full_name')
        candidate_full_name = frappe.db.get_value('Candidate', doc.candidate, 'full_name')

        # Construct the Adaptive Card JSON
        card_payload = {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"**@HR_admin**, Verdict for **{doc.current_round}** interview round (**{doc.name}**) has been submitted.",
                    "size": "medium",
                    "wrap" : True,
                },
                {
                    "type": "TextBlock",
                    "text": f"_Verdict_: **{doc.outcome}**",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": f"_Interviewer_: **{interviewer_full_name}**",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": f"_Candidate_: **{candidate_full_name}**",
                    "wrap": True
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "Interview Page",
                    "url": f"http://localhost:8000/app/interview/{doc.name}"
                },
                {
                    "type": "Action.OpenUrl",
                    "title": f"Candidate Page",
                    "url": f"http://localhost:8000/app/candidate/{doc.candidate}"
                },
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.3"
        }
        card_data = json.dumps(card_payload)
        send_teams_notification(card_data)


def send_reschedule_confirmation(doc, method):
    if (doc.get_doc_before_save()) and (doc.has_value_changed("date")):
        interviewer_full_name = frappe.db.get_value('User', doc.interviewer, 'full_name')
        candidate_full_name = frappe.db.get_value('Candidate', doc.candidate, 'full_name')

        # Construct the Adaptive Card JSON for confirmation
        confirmation_card = {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"**@Interviewer**, The **{doc.current_round}** interview round (**{doc.name}**) has been rescheduled.",
                    "size": "medium",
                    "wrap" : True,
                },
                {
                    "type": "TextBlock",
                    "text": f"**New Date**: {doc.date}",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": f"**Interviewer**: {interviewer_full_name}",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": f"**Candidate**: {candidate_full_name}",
                    "wrap": True
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "Updated Interview Page",
                    "url": f"http://localhost:8000/app/interview/{doc.name}"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.3"
        }

        card_data = json.dumps(confirmation_card)
        send_teams_notification(card_data)
        
        

@frappe.whitelist(allow_guest=True)
def handle_reschedule_request(doc_name=None):
    """This function handles the reschedule request from the Teams button click"""
    if not doc_name:
        frappe.throw("Invalid document name provided")

    # Get the document and mark it for reschedule (or handle as needed)
    doc = frappe.get_doc("Interview", doc_name)
    interviewer_full_name = frappe.db.get_value('User', doc.interviewer, 'full_name')
    # Construct reschedule notification message
    reschedule_message = {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": f"**@HR_admin** Reschedule is requested for the **{doc.current_round}** interview round (**{doc.name}**).",
                "size": "medium",
                "wrap" : True,
            },
            {
                "type": "TextBlock",
                "text": f"_Interviewer_ : **{interviewer_full_name}**",
                "wrap": True
            },
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Reschedule Interview",
                "url": f"http://localhost:8000/app/interview/{doc.name}"
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3"
    }
    card_data = json.dumps(reschedule_message)
    send_teams_notification(card_data)

    html_content = """
    <html>
    <head>
        <title>Reschedule Request Submitted</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #f4f4f9;
            }
            h1 {
                color: #4CAF50;
            }
            p {
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <h1>Thank You!</h1>
        <p>Your request for reschedule has been submitted successfully.</p>
        <p>You can now close this window.</p>
    </body>
    </html>
    """
    
    response = build_response("text/html", html_content)

    # Return the HTML response
    return response

