from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Commande, LigneCommande, Produit, Utilisateur
from datetime import datetime
import json

commande_bp = Blueprint('commande', __name__)


@commande_bp.route('/commande/recapitulatif')
@login_required
def recapitulatif():
    """Affiche le récapitulatif de la commande avant paiement"""
    panier = session.get('panier', {})

    if not panier:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('panier.voir_panier'))

    produits = []
    total = 0

    for produit_id, quantite in panier.items():
        produit = Produit.query.get(int(produit_id))
        if produit and produit.en_stock:
            sous_total = produit.prix_actuel * quantite
            total += sous_total
            produits.append({
                'produit': produit,
                'quantite': quantite,
                'sous_total': sous_total
            })
        else:
            flash(f'Le produit {produit.nom} n\'est plus disponible.', 'danger')
            return redirect(url_for('panier.voir_panier'))

    # Frais de livraison (offerts dès 50€)
    frais_livraison = 0 if total >= 50 else 5.90
    total_final = total + frais_livraison

    return render_template('commande/recapitulatif.html',
                           produits=produits,
                           total=total,
                           frais_livraison=frais_livraison,
                           total_final=total_final)


@commande_bp.route('/commande/valider', methods=['POST'])
@login_required
def valider_commande():
    """Valide la commande et crée l'entrée en base de données"""
    panier = session.get('panier', {})

    if not panier:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('panier.voir_panier'))

    # Récupérer les données du formulaire
    email = request.form.get('email', current_user.email)
    prenom = request.form.get('prenom', current_user.prenom or '')
    nom = request.form.get('nom', current_user.nom or '')
    telephone = request.form.get('telephone', '')
    adresse = request.form.get('adresse', '')
    ville = request.form.get('ville', '')
    code_postal = request.form.get('code_postal', '')
    pays = request.form.get('pays', 'France')
    notes = request.form.get('notes', '')

    # Vérifier que les champs obligatoires sont remplis
    if not all([prenom, nom, adresse, ville, code_postal]):
        flash('Veuillez remplir tous les champs obligatoires.', 'danger')
        return redirect(url_for('commande.recapitulatif'))

    # Calculer les totaux
    produits = []
    total = 0

    for produit_id, quantite in panier.items():
        produit = Produit.query.get(int(produit_id))
        if produit:
            sous_total = produit.prix_actuel * quantite
            total += sous_total
            produits.append({
                'produit': produit,
                'quantite': quantite,
                'sous_total': sous_total
            })

    frais_livraison = 0 if total >= 50 else 5.90
    total_final = total + frais_livraison

    # Créer la commande
    commande = Commande(
        utilisateur_id=current_user.id,
        email=email,
        prenom=prenom,
        nom=nom,
        telephone=telephone,
        adresse_livraison=f"{adresse}\n{code_postal} {ville}\n{pays}",
        ville=ville,
        code_postal=code_postal,
        pays=pays,
        sous_total=total,
        frais_livraison=frais_livraison,
        total=total_final,
        statut='en_attente'
    )

    db.session.add(commande)
    db.session.flush()  # Pour obtenir l'ID de la commande

    # Créer les lignes de commande
    for item in produits:
        ligne = LigneCommande(
            commande_id=commande.id,
            produit_id=item['produit'].id,
            nom_produit=item['produit'].nom,
            prix_unitaire=item['produit'].prix_actuel,
            quantite=item['quantite']
        )
        db.session.add(ligne)

        # Mettre à jour le stock
        produit = item['produit']
        produit.stock -= item['quantite']
        if produit.stock <= 0:
            produit.est_disponible = False

    # ============================================
    # GÉNÉRER LE QR CODE
    # ============================================
    from app.services.qrcode_service import generer_qr_code
    try:
        qr_path = generer_qr_code(commande)
        commande.qr_code = qr_path
        print(f"✅ QR Code généré pour {commande.reference}")
    except Exception as e:
        print(f"❌ Erreur génération QR Code: {e}")

    db.session.commit()

    # Vider le panier
    session.pop('panier', None)

    # ============================================
    # ENVOYER LES NOTIFICATIONS
    # ============================================
    from app.services.notification_service import NotificationService
    try:
        NotificationService.envoyer_email_commande(commande, commande.email)
        NotificationService.envoyer_email_admin(commande)
    except Exception as e:
        print(f"Erreur d'envoi de notification: {e}")

    flash(f'Commande #{commande.reference} créée avec succès !', 'success')
    return redirect(url_for('paypal.checkout', commande_id=commande.id))


@commande_bp.route('/commande/suivi/<reference>')
def suivi(reference):
    """Page de suivi d'une commande (publique)"""
    commande = Commande.query.filter_by(reference=reference).first_or_404()
    return render_template('commande/suivi.html', commande=commande)


@commande_bp.route('/commande/confirmation/<int:commande_id>')
@login_required
def confirmation(commande_id):
    """Page de confirmation après paiement"""
    commande = Commande.query.get_or_404(commande_id)

    # Vérifier que la commande appartient à l'utilisateur
    if commande.utilisateur_id != current_user.id and not current_user.est_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    # ============================================
    # GÉNÉRER LE QR CODE SI ABSENT
    # ============================================
    if not commande.qr_code:
        from app.services.qrcode_service import generer_qr_code
        try:
            qr_path = generer_qr_code(commande)
            commande.qr_code = qr_path
            db.session.commit()
            print(f"✅ QR Code généré pour la commande {commande.reference}")
        except Exception as e:
            print(f"❌ Erreur génération QR Code: {e}")

    return render_template('commande/confirmation.html', commande=commande)


@commande_bp.route('/commandes')
@login_required
def historique():
    """Historique des commandes de l'utilisateur"""
    commandes = Commande.query.filter_by(utilisateur_id=current_user.id) \
        .order_by(Commande.date_creation.desc()).all()
    return render_template('commande/historique.html', commandes=commandes)


@commande_bp.route('/commande/<int:commande_id>')
@login_required
def detail(commande_id):
    """Détail d'une commande"""
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id and not current_user.est_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    return render_template('commande/detail.html', commande=commande)


@commande_bp.route('/commande/modifier-statut/<int:commande_id>', methods=['POST'])
@login_required
def modifier_statut_commande(commande_id):
    """Modifie le statut d'une commande (admin uniquement)"""
    commande = Commande.query.get_or_404(commande_id)

    # Vérifier que l'utilisateur est admin
    if not current_user.est_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('commande.detail', commande_id=commande_id))

    nouveau_statut = request.form.get('statut')

    # Liste des statuts valides
    statuts_valides = ['en_attente', 'payee', 'preparation', 'expediee', 'livree', 'annulee']

    if nouveau_statut in statuts_valides:
        commande.statut = nouveau_statut
        db.session.commit()
        flash(f'Statut de la commande #{commande.reference} mis à jour : {nouveau_statut.replace("_", " ").title()}',
              'success')
    else:
        flash('Statut invalide.', 'danger')

    return redirect(url_for('commande.detail', commande_id=commande_id))

@commande_bp.route('/commande/facture/<int:commande_id>')
@login_required
def facture_pdf(commande_id):
    """Exporte la facture en PDF"""
    commande = Commande.query.get_or_404(commande_id)

    # Vérifier que la commande appartient à l'utilisateur
    if commande.utilisateur_id != current_user.id and not current_user.est_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    try:
        from app.services.pdf_service import PDFService
        pdf = PDFService.generer_facture(commande)

        # Créer la réponse avec current_app
        response = current_app.response_class(pdf, mimetype='application/pdf')
        response.headers.set('Content-Disposition',
                             f'attachment; filename=facture_{commande.reference}.pdf')
        response.headers.set('Content-Type', 'application/pdf')

        return response
    except Exception as e:
        print(f"❌ Erreur génération PDF: {e}")
        flash('Erreur lors de la génération du PDF.', 'danger')
        return redirect(url_for('commande.detail', commande_id=commande.id))
