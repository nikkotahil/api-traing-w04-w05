from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task
def send_poll_report_email(subject, message, to_email, file_path, file_name):
    html_message = render_to_string('polls/poll_report_email.html', {
        'message': message,
    })
    email = EmailMessage(
        subject=subject,
        body=html_message,
        to=[to_email],
    )
    email.content_subtype = 'html'
    email.attach_file(file_path)
    email.send()
    return "Email sent successfully"