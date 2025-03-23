from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from base.models.email import Email


def send_email(subject: str, receiver:str, template_name: str, template_context):
    sender = settings.DEFAULT_FROM_EMAIL
    message_html = render_to_string("emails/send-employe-password.html", context=template_context)
    email_db = Email.objects.create(
        subject=subject,
        content=message_html,
        receiver=receiver,
        template_name=template_name,
        template_context=template_context,
        sender=sender,
    )
    message_html = render_to_string(template_name, context=template_context)
    email = EmailMessage(
        subject,
        message_html,
        sender,
        [receiver],
    )
    email.content_subtype = "html"  # Indiquer que le contenu est en HTML

    try:
        email.send()
    except Exception as e:
        print(e)
        email_db.error = e
        email_db.save()