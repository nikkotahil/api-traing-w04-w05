from celery import shared_task
from django.core.mail import EmailMessage

@shared_task
def send_poll_report_email(subject, message, to_email, file_path, file_name):
    email = EmailMessage(subject, message, to=[to_email])
    email.attach_file(file_path)
    email.send()
    return "Email sent successfully"