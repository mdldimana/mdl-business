from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_required, current_user
import stripe
import os
from app import db
from app.models import Commande, LigneCommande, Produit

paiement_bp = Blueprint('paiement', __name__, url_prefix='/paiement')

# Configuration Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')


@login_required
def get_user_email():
    return current_user.email


@login_required
def get_user_name():
    return f"{current_user.prenom} {current_user.nom}".strip() or current_user.email


@paiement_bp.route('/checkout/<int:commande_id>')
@login_required
def checkout(commande_id):
    """Page de paiement Stripe"""
    commande = Commande.query.get_or_404(commande_id)

    # Vérifier que la commande appartient à l'utilisateur
    if commande.utilisateur_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    if commande.statut != 'en_attente':
        flash('Cette commande a déjà été traitée.', 'warning')
        return redirect(url_for('commande.detail', commande_id=commande.id))

    return render_template('paiement/checkout.html',
                           commande=commande,
                           stripe_public_key=STRIPE_PUBLIC_KEY)


@paiement_bp.route('/create-checkout-session/<int:commande_id>', methods=['POST'])
@login_required
def create_checkout_session(commande_id):
    """Crée une session de paiement Stripe"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id:
        return jsonify({'error': 'Accès non autorisé'}), 403

    try:
        # Créer la session Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Commande #{commande.reference}',
                        'description': f'MDL Business - {len(commande.lignes)} article(s)',
                    },
                    'unit_amount': int(commande.total * 100),  # Stripe utilise les cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('paiement.paiement_reussi', commande_id=commande.id, _external=True),
            cancel_url=url_for('paiement.paiement_annule', commande_id=commande.id, _external=True),
            customer_email=current_user.email,
            metadata={
                'commande_id': str(commande.id),
                'utilisateur_id': str(current_user.id)
            }
        )

        # Enregistrer l'ID de session
        commande.stripe_session_id = checkout_session.id
        db.session.commit()

        return jsonify({'session_id': checkout_session.id, 'url': checkout_session.url})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@paiement_bp.route('/succes/<int:commande_id>')
@login_required
def paiement_reussi(commande_id):
    """Page de succès après paiement"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    # Vérifier le statut du paiement via Stripe
    if commande.stripe_session_id:
        try:
            session = stripe.checkout.Session.retrieve(commande.stripe_session_id)
            if session.payment_status == 'paid':
                commande.statut = 'payee'
                commande.mode_paiement = 'stripe'
                commande.transaction_id = session.payment_intent
                db.session.commit()
                flash('Paiement confirmé ! Merci pour votre commande.', 'success')
            else:
                flash('Le paiement n\'a pas encore été confirmé.', 'warning')
        except Exception as e:
            flash('Erreur lors de la vérification du paiement.', 'danger')

    return redirect(url_for('commande.confirmation', commande_id=commande.id))


@paiement_bp.route('/annule/<int:commande_id>')
@login_required
def paiement_annule(commande_id):
    """Page d'annulation du paiement"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    flash('Le paiement a été annulé. Vous pouvez réessayer quand vous voulez.', 'warning')
    return redirect(url_for('paiement.checkout', commande_id=commande.id))


@paiement_bp.route('/webhook', methods=['POST'])
def webhook():
    """Webhook Stripe pour confirmer les paiements"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    # Traiter l'événement
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        commande_id = session.get('metadata', {}).get('commande_id')

        if commande_id:
            commande = Commande.query.get(int(commande_id))
            if commande:
                commande.statut = 'payee'
                commande.mode_paiement = 'stripe'
                commande.transaction_id = session.get('payment_intent')
                db.session.commit()

    return jsonify({'status': 'success'}), 200