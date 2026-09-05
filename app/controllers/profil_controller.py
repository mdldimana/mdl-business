from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import Utilisateur, Commande

# ATTENTION : CORRIGER prof1l_bp → profil_bp
profil_bp = Blueprint('profil', __name__, url_prefix='/profil')


@profil_bp.route('/')
@login_required
def index():
    commandes = Commande.query.filter_by(utilisateur_id=current_user.id) \
        .order_by(Commande.date_creation.desc()).all()

    return render_template('profil/index.html',
                           utilisateur=current_user,
                           commandes=commandes)


@profil_bp.route('/modifier', methods=['POST'])
@login_required
def modifier():
    email = request.form.get('email')
    telephone = request.form.get('telephone')

    if email and email != current_user.email:
        existant = Utilisateur.query.filter(
            Utilisateur.email == email,
            Utilisateur.id != current_user.id
        ).first()
        if existant:
            flash('Cet email est déjà utilisé par un autre compte.', 'danger')
            return redirect(url_for('profil.index'))

        current_user.email = email
        flash('Email modifié avec succès.', 'success')

    if telephone is not None:
        current_user.telephone = telephone
        flash('Téléphone modifié avec succès.', 'success')

    db.session.commit()
    return redirect(url_for('profil.index'))


@profil_bp.route('/commande/<int:commande_id>')
@login_required
def detail_commande(commande_id):
    commande = Commande.query.get_or_404(commande_id)

    if commande.utilisateur_id != current_user.id and not current_user.est_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('profil.index'))

    return render_template('profil/detail_commande.html', commande=commande)