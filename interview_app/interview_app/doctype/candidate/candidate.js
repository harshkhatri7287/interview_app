// // In your_app/public/js/candidate.js
frappe.ui.form.on('Candidate', {

    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frappe.call({
                method: 'interview_app.interview_app.doctype.candidate.candidate.fetch_candidate_interviews',
                args: {
                    candidate_id: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table('interview_rounds');
                        r.message.forEach(interview => {
                            let row = frm.add_child('interview_rounds');
                            row.interview_round = interview.current_round;
                            row.outcome = interview.outcome;
                            row.interviewer = interview.interviewer;
                            row.date = interview.date;
                        });

                        frm.refresh_field('interview_rounds');
                    }
                }
            });

            frm.add_custom_button(__('Schedule Next Interview'), function() {
                schedule_next_interview(frm);
            });
        }
    },
});

function schedule_next_interview(frm) {
    frappe.call({
        method: 'interview_app.interview_app.doctype.candidate.candidate.fetch_candidate_interviews',
        args: {
            candidate_id: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                var rounds = r.message;
                console.log("Fetched rounds:", rounds);

                var last_round = rounds.length > 0 ? rounds[rounds.length - 1] : null;
                var next_round = get_next_round(rounds);

                if (last_round) {
                    if (last_round.outcome === 'Pending') {
                        frappe.msgprint(__('The ' + last_round.current_round + ' interview round is still pending. Please complete it before scheduling the next one.'));
                        return;
                    }
                }

                if (next_round) {
                    frappe.new_doc('Interview', {
                        'candidate': frm.doc.name,
                        'current_round': next_round,
                    });
                } else {
                    frappe.msgprint(__('All interview rounds are completed.'));
                }
            } else {
                frappe.new_doc('Interview', {
                    'candidate': frm.doc.name,
                    'current_round': 'Screening',
                });
            }
        }
    });
}

function get_next_round(rounds) {
    var completed_rounds = rounds.map(round => round.current_round);
    var all_rounds = ['Screening', 'Aptitude', 'Technical', 'HR'];
    for (var i = 0; i < all_rounds.length; i++) {
        if (!completed_rounds.includes(all_rounds[i])) {
            return all_rounds[i];
        }
    }
    return null;
}


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