from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_required, current_user
import os
import requests
import json
from app import db
from app.models import Commande, LigneCommande, Produit

paypal_bp = Blueprint('paypal', __name__, url_prefix='/paypal')

# Configuration PayPal (mode sandbox pour les tests)
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET')

if PAYPAL_MODE == 'sandbox':
    PAYPAL_API_URL = "https://api-m.sandbox.paypal.com"
else:
    PAYPAL_API_URL = "https://api-m.paypal.com"


def get_paypal_access_token():
    """Récupère un token d'accès PayPal"""
    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    data = {'grant_type': 'client_credentials'}

    try:
        response = requests.post(
            f"{PAYPAL_API_URL}/v1/oauth2/token",
            auth=auth,
            headers=headers,
            data=data
        )
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Erreur PayPal: {e}")
        return None


@paypal_bp.route('/checkout/<int:commande_id>')
@login_required
def checkout(commande_id):
    """Page de paiement PayPal"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    if commande.statut != 'en_attente':
        flash('Cette commande a déjà été traitée.', 'warning')
        return redirect(url_for('commande.detail', commande_id=commande.id))

    return render_template('paypal/checkout.html',
                           commande=commande,
                           paypal_client_id=PAYPAL_CLIENT_ID,
                           paypal_mode=PAYPAL_MODE)


@paypal_bp.route('/creer-commande/<int:commande_id>', methods=['POST'])
@login_required
def creer_commande_paypal(commande_id):
    """Crée une commande PayPal"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id:
        return jsonify({'error': 'Accès non autorisé'}), 403

    # Obtenir le token d'accès
    access_token = get_paypal_access_token()
    if not access_token:
        return jsonify({'error': 'Impossible de se connecter à PayPal'}), 500

    # Créer la commande PayPal
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    # URL de retour après paiement
    return_url = url_for('paypal.paiement_reussi', commande_id=commande.id, _external=True)
    cancel_url = url_for('paypal.paiement_annule', commande_id=commande.id, _external=True)

    data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": commande.reference,
            "description": f"Commande #{commande.reference} - MDL Business",
            "amount": {
                "currency_code": "USD",
                "value": f"{commande.total:.2f}"
            }
        }],
        "application_context": {
            "brand_name": "MDL Business",
            "landing_page": "BILLING",
            "user_action": "PAY_NOW",
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    }

    try:
        response = requests.post(
            f"{PAYPAL_API_URL}/v2/checkout/orders",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        order_data = response.json()

        # Enregistrer l'ID de la commande PayPal
        commande.transaction_id = order_data['id']
        db.session.commit()

        # Trouver le lien d'approbation
        approval_url = None
        for link in order_data.get('links', []):
            if link.get('rel') == 'approve':
                approval_url = link.get('href')
                break

        if not approval_url:
            return jsonify({'error': 'URL d\'approbation non trouvée'}), 500

        return jsonify({'approval_url': approval_url})

    except Exception as e:
        print(f"Erreur PayPal: {e}")
        return jsonify({'error': str(e)}), 500


@paypal_bp.route('/succes/<int:commande_id>')
@login_required
def paiement_reussi(commande_id):
    """Page de succès après paiement PayPal"""
    commande = Commande.query.get_or_404(commande_id)
    payer_id = request.args.get('PayerID')
    token = request.args.get('token')

    if commande.utilisateur_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    if token and token != commande.transaction_id:
        flash('Erreur de validation du paiement.', 'danger')
        return redirect(url_for('paypal.checkout', commande_id=commande.id))

    # Capturer le paiement
    if payer_id and token:
        access_token = get_paypal_access_token()
        if access_token:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }

            try:
                response = requests.post(
                    f"{PAYPAL_API_URL}/v2/checkout/orders/{token}/capture",
                    headers=headers
                )
                response.raise_for_status()
                capture_data = response.json()

                if capture_data.get('status') == 'COMPLETED':
                    commande.statut = 'payee'
                    commande.mode_paiement = 'paypal'
                    commande.transaction_id = token
                    db.session.commit()
                    flash('Paiement confirmé ! Merci pour votre commande.', 'success')
                else:
                    flash('Le paiement n\'a pas été finalisé.', 'warning')

            except Exception as e:
                print(f"Erreur capture PayPal: {e}")
                flash('Erreur lors de la confirmation du paiement.', 'danger')

    return redirect(url_for('commande.confirmation', commande_id=commande.id))


@paypal_bp.route('/annule/<int:commande_id>')
@login_required
def paiement_annule(commande_id):
    """Page d'annulation du paiement"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    flash('Le paiement a été annulé. Vous pouvez réessayer quand vous voulez.', 'warning')
    return redirect(url_for('paypal.checkout', commande_id=commande.id))


@paypal_bp.route('/paiement-test/<int:commande_id>', methods=['POST'])
@login_required
def paiement_test(commande_id):
    """Simule un paiement réussi pour les tests"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    # Simuler un paiement réussi
    commande.statut = 'payee'
    commande.mode_paiement = 'test'
    commande.transaction_id = f'TEST-{commande.reference}'
    db.session.commit()

    flash('✅ Paiement test réussi ! Commande confirmée.', 'success')
    return redirect(url_for('commande.confirmation', commande_id=commande.id))