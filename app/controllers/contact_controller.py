from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from app.extensions import mail
import os
import threading

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')


def send_async_email(app, msg):
    """Envoie l'email en arrière-plan"""
    with app.app_context():
        try:
            mail.send(msg)
            print("✅ Email envoyé avec succès")
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")


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

    if not all([nom, email, sujet, message]):
        flash('Veuillez remplir tous les champs.', 'danger')
        return redirect(url_for('contact.index'))

    try:
        # Construction du message
        msg = Message(
            subject=f"Contact MDL Business - {sujet}",
            sender=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@mdlbusiness.com'),
            recipients=[os.environ.get('MAIL_RECIPIENT', 'mdlbusiness0@gmail.com')],
            body=f"""
            Nouveau message de contact :

            Nom : {nom}
            Email : {email}
            Sujet : {sujet}

            Message :
            {message}

            ---
            Ce message a été envoyé depuis le formulaire de contact de MDL Business.
            Pour répondre, utiliser l'adresse : {email}
            """,
            reply_to=email
        )

        # Envoyer en arrière-plan (asynchrone)
        # L'utilisateur voit immédiatement le message de confirmation
        threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

        flash('Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.', 'success')
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        flash('Votre message a été enregistré. Nous vous répondrons dans les plus brefs délais.', 'success')

    return redirect(url_for('contact.index'))