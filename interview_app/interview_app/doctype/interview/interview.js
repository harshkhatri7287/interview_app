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

    onload: function(frm) {
        frm.refresh_field('problems');
    },
    refresh: function(frm) {
        frm.refresh_field('problems');
    },

    // Generate Screening or Technical Round questions
    refresh: function(frm) {
        frm.add_custom_button(__('Generate Questions'), function() {
            if (frappe.user.has_role('HR')) {
                frm.disable_custom_button(__('Generate Questions'));
            }
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
        if (frm.doc.current_round === 'Technical') {
            frm.add_custom_button(__('Evaluate Problems'), function() {
                if (frappe.user.has_role('HR')) {
                    frm.disable_custom_button(__('Evaluate Problems'));
                }
                frappe.show_alert("Evaluating problems...Please wait")
                frappe.call({
                    method: 'interview_app.interview_app.doctype.candidate.candidate.evaluate_problems',
                    args: {
                        interview_id: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint("Evaluation Done!!");
                        }
                    }
                });
            });
        }
        // frm.add_custom_button(__('Reschedule Request'), function() {
        //     if (frappe.user.has_role('HR')) {
        //         frm.disable_custom_button(__('Generate Questions'));
        //     }
        //     let d = new frappe.ui.Dialog({
        //         title: 'Request Reschedule',
        //         fields: [
        //             {
        //                 label: 'Preferred Date',
        //                 fieldname: 'preferred_date',
        //                 fieldtype: 'Date',
        //                 reqd: 1
        //             },
        //         ],
        //         primary_action_label: 'Submit',
        //         primary_action(values) {
        //              frappe.call({
        //                 method: 'interview_app.interview_app.doctype.interview.interview.create_interview_reschedule',
        //                 args: {
        //                     interview_id: frm.doc.name,
        //                     preferred_date: values.preferred_date,
        //                 },
        //                 callback: function(r) {
        //                     if (r.message) {
        //                         frappe.msgprint(__('Reschedule request created successfully'));
        //                     }
        //                 }
        //             });
        //             d.hide();
        //         }
        //     });
        //     d.show();
        // });
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
                frappe.show_alert(__('Candidate status updated to ' + r.message));
            }
        }
    });
}


// TIMER

function showTimer(duration = 30) {
    let timeLeft = duration;
    let totalDuration = duration; 
    frappe.show_progress(
        'Generating questions...',  
        0,                          
        100,                         
        `${timeLeft} seconds remaining` 
    );
    const timerInterval = setInterval(() => {
        timeLeft--;
        let progressPercent = ((totalDuration - timeLeft) * 100) / totalDuration;
        frappe.show_progress(
            'Generating questions...',  
            progressPercent,             
            100,                       
            `${timeLeft} seconds remaining`  
        );
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            frappe.hide_progress();
        }
    }, 1000);
    return timerInterval;
}

function stopTimer(timerInterval) {
    if (timerInterval) {
        clearInterval(timerInterval);
        frappe.hide_progress(); 
    }
}


// GENERATE CODING QUESTIONS
function show_generate_question_dialog(frm) {
    console.log('Open Dialog!');
    let dialog = new frappe.ui.Dialog({
        title: 'Generate Coding Questions',
        fields: [
            {
                label: 'Type of Problem',
                fieldname: 'problem_type',
                fieldtype: 'Select',
                options: ['Debug & Correction', 'Adding a Feature', 'DSA', 'Code Optimization'],
                reqd: 1
            },
        ],
        primary_action_label: 'Generate',
        primary_action(values) {
            dialog.hide();
            frappe.show_alert(__('Generating question...'));
            generate_coding_question(frm.doc.candidate, values.problem_type, frm);
        }
    });

    dialog.show();
}

function generate_coding_question(candidate, problem_type, frm) {
    frappe.call({
        method: 'interview_app.interview_app.doctype.candidate.candidate.generate_coding_question',
        args: {
            candidate: candidate,
            problem_type: problem_type,
        },
        callback: function(r) {
            if (r.message) {
                let question = r.message;
                console.log("Generated Questions..");
                let question_dialog = new frappe.ui.Dialog({
                    title: 'Generated Question',
                    fields: [
                        {
                            label: 'Problem Statement',
                            fieldname: 'problem_statement',
                            fieldtype: 'Text',
                            default: question.problem_statement,
                            read_only: 1
                        },
                    ],
                    primary_action_label: 'Proceed',
                    primary_action(values) {
                        question_dialog.hide();
                        add_coding_problem_to_child_table(frm, candidate, question.problem_statement, question.problem_code);
                    }
                });

                question_dialog.set_secondary_action_label('Generate Again');
                question_dialog.set_secondary_action(() => {
                    question_dialog.hide();
                    show_generate_question_dialog(frm);
                });

                question_dialog.show();
            }
        }
    });
}


function add_coding_problem_to_child_table(frm, candidate, problem_statement, problem_code) {
    // Call server-side function to save the coding problem
    frappe.call({
        method: 'interview_app.interview_app.doctype.candidate.candidate.save_coding_problem',
        args: {
            interview_id: frm.doc.name,
            candidate: candidate,
            problem_statement: problem_statement,
            problem_code: problem_code
        },
        callback: function(r) {
            if (r.message.status === "success") {
                // Add the new problem to the child table
                frm.add_child('problems', {
                    candidate: candidate,
                    problem_statement: problem_statement,
                    problem_code: problem_code,
                    interviewer: frappe.session.user
                });

                // Refresh the child table
                frm.refresh_field('problems');
                frappe.show_alert(__('Coding problem added successfully to the table.'));
            } else {
                frappe.msgprint(__('Error adding coding problem: ' + r.message.message));
            }
        }
    });
}