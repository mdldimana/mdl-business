import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for
from datetime import datetime


class NotificationService:
    """Service d'envoi de notifications"""

    @staticmethod
    def envoyer_email_commande(commande, email_utilisateur):
        """
        Envoie un email de confirmation de commande
        """
        # Configuration SMTP (pour tests, on utilise un fichier)
        # En production, utilisez SendGrid ou autre service

        sujet = f"MDL Business - Confirmation de commande #{commande.reference}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0b2b4a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; }}
                .btn {{ background: #2d7aff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .total {{ font-size: 24px; color: #2d7aff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MDL Business</h1>
                    <p>Confirmation de commande</p>
                </div>
                <div class="content">
                    <h2>Merci pour votre commande !</h2>
                    <p>Bonjour {commande.prenom},</p>
                    <p>Nous confirmons la réception de votre commande <strong>#{commande.reference}</strong>.</p>

                    <h3>Récapitulatif</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 10px; text-align: left;">Produit</th>
                            <th style="padding: 10px; text-align: center;">Quantité</th>
                            <th style="padding: 10px; text-align: right;">Prix</th>
                        </tr>
                        {''.join([f'<tr><td style="padding: 10px;">{ligne.nom_produit}</td><td style="padding: 10px; text-align: center;">{ligne.quantite}</td><td style="padding: 10px; text-align: right;">{ligne.prix_unitaire * ligne.quantite}$</td></tr>' for ligne in commande.lignes])}
                        <tr style="border-top: 2px solid #dee2e6;">
                            <td colspan="2" style="padding: 10px; text-align: right;"><strong>Total</strong></td>
                            <td style="padding: 10px; text-align: right;"><span class="total">{commande.total}$</span></td>
                        </tr>
                    </table>

                    <div style="margin-top: 20px;">
                        <h4>Adresse de livraison</h4>
                        <p>
                            {commande.prenom} {commande.nom}<br>
                            {commande.adresse_livraison.replace(chr(10), '<br>')}<br>
                            {commande.code_postal} {commande.ville}<br>
                            {commande.pays}
                        </p>
                    </div>

                    <div style="margin-top: 20px; text-align: center;">
                        <a href="{url_for('commande.suivi', reference=commande.reference, _external=True)}" class="btn">
                            Suivre ma commande
                        </a>
                    </div>

                    <p style="margin-top: 20px; color: #6c757d; font-size: 14px;">
                        Vous pouvez suivre votre commande à tout moment en utilisant le lien ci-dessus.
                    </p>
                </div>
                <div class="footer">
                    <p>MDL Business - Tous droits réservés</p>
                    <p>Cet email est un envoi automatique, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # En mode développement, on affiche l'email dans la console
        print(f"📧 EMAIL ENVOYÉ À {email_utilisateur}")
        print(f"Sujet: {sujet}")
        print(f"Contenu: {html[:500]}...")

        return True

    @staticmethod
    def envoyer_email_admin(commande):
        """
        Envoie une notification à l'admin pour une nouvelle commande
        """
        print(f"🔔 NOUVELLE COMMANDE #{commande.reference}")
        print(f"Total: {commande.total}$ - Client: {commande.prenom} {commande.nom}")
        return True