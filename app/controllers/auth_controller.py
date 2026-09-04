from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import Utilisateur
from app.forms import ConnexionForm
from datetime import datetime

# ICI : enlever le préfixe url_prefix pour le moment
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))

    form = ConnexionForm()
    if form.validate_on_submit():
        utilisateur = Utilisateur.query.filter_by(email=form.email.data).first()

        if utilisateur and bcrypt.check_password_hash(utilisateur.mot_de_passe_hash, form.mot_de_passe.data):
            login_user(utilisateur, remember=form.se_souvenir.data)
            utilisateur.date_derniere_connexion = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            flash('Connexion réussie !', 'success')
            return redirect(next_page) if next_page else redirect(url_for('accueil'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('auth/connexion.html', form=form)


@auth_bp.route('/deconnexion')
@login_required
def deconnexion():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('accueil'))


from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import Utilisateur
from app.forms import ConnexionForm, InscriptionForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))

    form = ConnexionForm()
    if form.validate_on_submit():
        utilisateur = Utilisateur.query.filter_by(email=form.email.data).first()

        if utilisateur and bcrypt.check_password_hash(utilisateur.mot_de_passe_hash, form.mot_de_passe.data):
            login_user(utilisateur, remember=form.se_souvenir.data)
            utilisateur.date_derniere_connexion = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            flash('Connexion réussie !', 'success')
            return redirect(next_page) if next_page else redirect(url_for('accueil'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('auth/connexion.html', form=form)


@auth_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """Page d'inscription des nouveaux utilisateurs"""
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))

    form = InscriptionForm()
    if form.validate_on_submit():
        # Vérifier si l'email existe déjà (validation déjà faite par le formulaire)

        # Créer le nouvel utilisateur
        mot_de_passe_hash = bcrypt.generate_password_hash(form.mot_de_passe.data).decode('utf-8')

        utilisateur = Utilisateur(
            email=form.email.data,
            prenom=form.prenom.data,
            nom=form.nom.data,
            mot_de_passe_hash=mot_de_passe_hash,
            est_admin=False,
            est_actif=True
        )

        db.session.add(utilisateur)
        db.session.commit()

        # Connecter automatiquement l'utilisateur
        login_user(utilisateur)

        flash(f'Bienvenue {utilisateur.prenom} ! Votre compte a été créé avec succès.', 'success')
        return redirect(url_for('accueil'))

    return render_template('auth/inscription.html', form=form)


@auth_bp.route('/deconnexion')
@login_required
def deconnexion():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('accueil'))