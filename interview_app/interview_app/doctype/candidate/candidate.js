// // In your_app/public/js/candidate.js
frappe.ui.form.on('Candidate', {

    refresh: function(frm) {
        // Ensure the document is not new
        if (!frm.doc.__islocal) {
            // Call the server-side method to fetch interviews
            frappe.call({
                method: 'interview_app.interview_app.doctype.candidate.candidate.fetch_candidate_interviews',
                args: {
                    candidate_id: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing child table data
                        frm.clear_table('interview_rounds');

                        // Populate the child table with fetched data
                        r.message.forEach(interview => {
                            let row = frm.add_child('interview_rounds');
                            row.interview_round = interview.current_round;
                            row.outcome = interview.outcome;
                            row.interviewer = interview.interviewer;
                            row.date = interview.date;
                        });

                        // Refresh the form to display the updated child table
                        frm.refresh_field('interview_rounds');
                    }
                }
            });

            frm.add_custom_button(__('Schedule Next Interview'), function() {
                schedule_next_interview(frm);
            });

            frm.add_custom_button(__('Generate Questions'), function() {
                frappe.call({
                    method: 'interview_app.interview_app.doctype.candidate.candidate.generate_questions',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            // frappe.msgprint(__('Questions generated and added successfully.'));
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
    },
});

function schedule_next_interview(frm) {
    // Fetch the interview details for the candidate
    frappe.call({
        method: 'interview_app.interview_app.doctype.candidate.candidate.get_interview_rounds',
        args: {
            candidate: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                var completed_rounds = r.message.completed_rounds;
                var next_round = get_next_round(completed_rounds);

                if (next_round) {
                    if (completed_rounds.includes(next_round)) {
                        frappe.msgprint(__(next_round + ' round is already scheduled or completed.'));
                    } else {
                        frappe.new_doc('Interview', {
                            'candidate': frm.doc.name,
                            'current_round': next_round,
                        });
                    }
                } else {
                    frappe.msgprint(__('All interview rounds are completed.'));
                }
            }
        }
    });
}

function get_next_round(completed_rounds) {
    var rounds = ['Screening', 'Aptitude', 'Technical', 'HR'];
    for (var i = 0; i < rounds.length; i++) {
        if (!completed_rounds.includes(rounds[i])) {
            return rounds[i];
        }
    }
    return null;
}