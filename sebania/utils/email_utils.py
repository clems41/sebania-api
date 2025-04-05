from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging

from base.models import User, Ferme
from base.models.email import Email

# Get an instance of a logger
logger = logging.getLogger(__name__)

def send_email_to_new_employe(ferme: Ferme, employe: User, employe_password: str):
    """
    Envoi d'un email lors de la création d'un nouvel employé pour une ferme
    """
    subject = "Bienvenue sur sebania"
    template_context = {
        "employe_prenom": employe.first_name,
        "responsable_prenom": ferme.responsable.first_name,
        "nom_ferme": ferme.nom,
        "app_url": "TODO",
        "password_employe": employe_password,
    }
    template_name = "emails/send-employe-password.html"
    _send_email(subject, employe.email, template_name, template_context)

def send_reset_password(user: User, new_password: str):
    """
    Envoi d'un nouveau mot de passe à un utilisateur l'ayant oublié
    """
    subject = "[Sebania] Réinitialisation de votre mot de passe"
    template_context = {
        "user_prenom": user.first_name,
        "new_password": new_password,
    }
    template_name = "emails/reset-password.html"
    _send_email(subject, user.email, template_name, template_context)

def send_feedback_to_super_users(sender: User, sujet: str, message: str):
    """
    Envoi d'un email aux super users lors d'un feedback utilisateur
    """
    super_users = User.objects.filter(is_superuser=True)
    subject = "[Sebania] Nouveau retour d'un utilisateur"
    template_context = {
        "prenom": sender.first_name,
        "nom": sender.last_name,
        "message": message,
        "sujet": sujet,
    }
    template_name = "emails/send-feedback.html"
    if len(super_users) == 0:
        logger.error("Aucun super utilisateur a été trouvé en base, le retour utilisateur ne pourra donc pas être envoyé")
    for user in super_users:
        _send_email(subject=subject, receiver=user.email, template_name=template_name, template_context=template_context)








def _send_email(subject: str, receiver:str, template_name: str, template_context):
    sender = settings.DEFAULT_FROM_EMAIL
    message_html = render_to_string(template_name, context=template_context)
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
        logger.error(e)
        email_db.error = e
        email_db.save()