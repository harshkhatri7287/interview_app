// Copyright (c) 2024, Harsh and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Interview", {
// 	refresh(frm) {

// 	},
// });
frappe.listview_settings['Interview'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Get Questions'), function() {
            const selected = listview.get_checked_items();
            if (selected.length > 0) {
                selected.forEach(item => {
                    frappe.call({
                        method: 'interview_app.interview_app.doctype.question.question.get_questions',
                        args: {
                            candidate: item.name
                        },
                        callback: function(r) {
                            if (r.message) {
                                let questions = JSON.parse(r.message);
                                let questions_html = '<ol>';
                                questions.forEach(q => {
                                    questions_html += `<li>${q}</li>`;
                                });
                                questions_html += '</ol>';
                                frappe.msgprint(questions_html, 'Interview Questions for ' + item.name);
                            }
                        }
                    });
                });
            } else {
                frappe.msgprint('Please select an interview to get questions.');
            }
        });
    }
};
