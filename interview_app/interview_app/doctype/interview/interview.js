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

