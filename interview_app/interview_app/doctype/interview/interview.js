// Copyright (c) 2024, Harsh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Interview", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Interview', {
        refresh: function(frm) {
            const isInterviewer = frappe.user.has_role("Interviewer");
            const isAdmin = frappe.user.has_role("System Manager") || frappe.session.user === 'Administrator';

            if (isInterviewer && !isAdmin) {
                if (frm.doc.interviewer !== frappe.session.user) {
                    frm.disable_save();
                    frappe.msgprint(__('You are not allowed to edit this interview.'));
                }
            }
        },
    after_save: function(frm) {
        update_candidate_status(frm);
    },

    validate: function(frm) {
        update_candidate_status(frm);
    },

    refresh: function(frm) {
        frm.add_custom_button(__('Reschedule Request'), function() {
            let d = new frappe.ui.Dialog({
                title: 'Request Reschedule',
                fields: [
                    {
                        label: 'Preferred Date',
                        fieldname: 'preferred_date',
                        fieldtype: 'Date',
                        reqd: 1
                    },
                    {
                        label: 'Preferred Time',
                        fieldname: 'preferred_time',
                        fieldtype: 'Time',
                        reqd: 1
                    }
                ],
                primary_action_label: 'Submit',
                primary_action(values) {
                     frappe.call({
                        method: 'interview_app.interview_app.doctype.interview.interview.create_interview_reschedule',
                        args: {
                            interview_id: frm.doc.name,
                            preferred_date: values.preferred_date,
                            preferred_time: values.preferred_time
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.msgprint(__('Reschedule request created successfully'));
                            }
                        }
                    });
                    d.hide();
                }
            });
            d.show();
        });
    }
    
});

function update_candidate_status(frm) {
    frappe.call({
        method: 'interview_app.interview_app.doctype.interview.interview.update_candidate_status_client',
        args: {
            candidate: frm.doc.candidate
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint(__('Candidate status updated to ' + r.message));
            }
        }
    });
}

