// Copyright (c) 2024, Harsh and contributors
// For license information, please see license.txt


frappe.ui.form.on('Interview', {

    // Necessary validation for interviewer
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

    // Update canndidate status
    after_save: function(frm) {
        update_candidate_status(frm);
    },
    
    // Generate Screening or Technical Round questions
    refresh: function(frm) {
        frm.add_custom_button(__('Generate Questions'), function() {
            if (frm.doc.current_round === "Screening" && frm.doc.outcome === "Pending") {
                var timerInterval = showTimer();

                frappe.call({
                    method: 'interview_app.interview_app.doctype.candidate.candidate.generate_questions',
                    args: {
                        docname: frm.doc.candidate
                    },
                    callback: function(r) {
                        stopTimer(timerInterval);
                        if (!r.exc) {
                            frm.reload_doc();
                        } else {
                            frappe.msgprint("Please try again.");
                        }
                    }
                });
            }
            else if (frm.doc.current_round === "Technical" && frm.doc.outcome === "Pending")
            {
                show_generate_question_dialog(frm);
            }
            else if (frm.doc.current_round === "Aptitude" || frm.doc.current_round === "HR"){
                frappe.msgprint("Currently Not generating question for this round!");
            }
            else {
                frappe.msgprint("Interview Should have Pending outcome!");
            }

            
        });
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
                ],
                primary_action_label: 'Submit',
                primary_action(values) {
                     frappe.call({
                        method: 'interview_app.interview_app.doctype.interview.interview.create_interview_reschedule',
                        args: {
                            interview_id: frm.doc.name,
                            preferred_date: values.preferred_date,
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


// TIMER
function showTimer() {
    var timeLeft = 30;

    // Display the initial message
    frappe.msgprint({
        message: `Generating questions... <span id="timer-countdown">${timeLeft}</span> seconds remaining.`,
        title: 'Please wait...',
        indicator: 'yellow'
    });

    var timerInterval = setInterval(function() {
        timeLeft--;
        // Update the countdown text
        $('#timer-countdown').text(timeLeft);

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            frappe.hide_msgprint();
        }
    }, 1000);

    return timerInterval;
}

function stopTimer(timerInterval) {
    clearInterval(timerInterval);
    frappe.hide_msgprint(); 
}

// GENERATE CODING QUESTIONS
function show_generate_question_dialog(frm) {
    console.log('Open Dialog!');
    let dialog = new frappe.ui.Dialog({
        title: 'Generate Coding Questions',
        fields: [
            {
                label: 'Type of Question',
                fieldname: 'question_type',
                fieldtype: 'Select',
                options: ['Debug & Correction', 'Adding a Feature', 'DSA', 'Code Optimization'],
                reqd: 1
            },
        ],
        primary_action_label: 'Generate',
        primary_action(values) {
            dialog.hide();
            generate_coding_question(frm.doc.candidate);
        }
    });

    dialog.show();
}

function generate_coding_question(candidate) {
    frappe.call({
        method: 'interview_app.interview_app.doctype.candidate.candidate.generate_coding_question',
        args: {
            candidate: candidate,
            // question_type: question_type,
            // skills: skills
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint(__('Question generated and saved successfully.'));
            }
        }
    });
}
