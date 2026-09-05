from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_mail import Message
from app import mail
import os

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')


@contact_bp.route('/')
def index():
    """Page de contact"""
    return render_template('contact/index.html')


@contact_bp.route('/envoyer', methods=['POST'])
def envoyer():
    """Envoie le message de contact"""
    nom = request.form.get('nom')
    email = request.form.get('email')
    sujet = request.form.get('sujet')
    message = request.form.get('message')

    # Validation simple
    if not all([nom, email, sujet, message]):
        flash('Veuillez remplir tous les champs.', 'danger')
        return redirect(url_for('contact.index'))

    # Envoyer l'email (si configuré)
    try:
        msg = Message(
            subject=f"Contact MDL Business - {sujet}",
            sender=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@mdlbusiness.com'),
            recipients=[os.environ.get('MAIL_RECIPIENT', 'mdlbusiness@gmail.com')],
            body=f"""
            Nouveau message de contact :

            Nom : {nom}
            Email : {email}
            Sujet : {sujet}

            Message :
            {message}
            """,
            reply_to=email
        )
        mail.send(msg)
        flash('Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.', 'success')
    except Exception as e:
        # En mode développement, afficher le message dans les logs
        print(f"⚠️ Email non envoyé (mail non configuré): {e}")
        flash('Votre message a été enregistré. Nous vous répondrons dans les plus brefs délais.', 'success')

    return redirect(url_for('contact.index'))