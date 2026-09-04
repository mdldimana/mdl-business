import os
from twilio.rest import Client
from flask import url_for


class WhatsAppService:
    def __init__(self):
        self.client = Client(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        self.from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        self.admin_number = os.environ.get('ADMIN_WHATSAPP', 'whatsapp:+243829018462')

    def envoyer_confirmation_commande(self, commande, numero_client):
        """Envoie une confirmation de commande avec les variables personnalisées"""
        try:
            message = self.client.messages.create(
                from_=self.from_number,
                to=f"whatsapp:{numero_client}",
                content_sid="HX350d429d32e64a552466cafecbe95f3c",  # Template ID
                content_variables=json.dumps({
                    "1": commande.reference,
                    "2": f"{commande.total:.2f} USD",
                    "3": commande.prenom
                })
            )
            print(f"✅ WhatsApp envoyé à {numero_client}")
            return True, message.sid
        except Exception as e:
            print(f"❌ Erreur WhatsApp: {e}")
            return False, str(e)

    def envoyer_lien_suivi(self, commande, numero_client):
        """Envoie le lien de suivi par WhatsApp"""
        try:
            lien_suivi = url_for('commande.suivi', reference=commande.reference, _external=True)

            message = self.client.messages.create(
                from_=self.from_number,
                to=f"whatsapp:{numero_client}",
                body=f"🔍 Suivez votre commande #{commande.reference} : {lien_suivi}"
            )
            print(f"✅ Lien de suivi envoyé à {numero_client}")
            return True, message.sid
        except Exception as e:
            print(f"❌ Erreur WhatsApp: {e}")
            return False, str(e)

    def envoyer_alerte_admin(self, commande):
        """Alerte l'admin d'une nouvelle commande"""
        try:
            message = f"🔔 Nouvelle commande !\n"
            message += f"📦 Réf: #{commande.reference}\n"
            message += f"👤 Client: {commande.prenom} {commande.nom}\n"
            message += f"💰 Total: {commande.total:.2f} USD\n"
            message += f"📅 Date: {commande.date_creation.strftime('%d/%m/%Y %H:%M')}"

            admin_msg = self.client.messages.create(
                from_=self.from_number,
                to=self.admin_number,
                body=message
            )
            print(f"✅ Alerte admin envoyée")
            return True, admin_msg.sid
        except Exception as e:
            print(f"❌ Erreur alerte admin: {e}")
            return False, str(e)