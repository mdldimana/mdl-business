from flask import Flask, render_template
import os
from dotenv import load_dotenv

from app.extensions import db, migrate, bcrypt, login_manager, cache, mail  # ← AJOUTER mail
from app.models import Utilisateur, Categorie, Produit

# ============================================
# IMPORT CLOUDINARY
# ============================================
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()


def create_app():
    app = Flask(__name__,
                template_folder='views/templates',
                static_folder='views/static')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    if not app.config['SQLALCHEMY_DATABASE_URI']:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}"
            f"@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}"
            f"/{os.environ.get('DB_NAME')}"
        )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ============================================
    # CLOUDINARY - CONFIGURATION
    # ============================================
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )

    # ============================================
    # CACHE DÉSACTIVÉ (PAS DE REDIS)
    # ============================================
    app.config['CACHE_TYPE'] = 'NullCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    # ============================================
    # CONFIGURATION MAIL (AJOUTER CE BLOC)
    # ============================================
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@mdlbusiness.com')

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    mail.init_app(app)  # ← AJOUTER CETTE LIGNE

    @login_manager.user_loader
    def load_user(user_id):
        return Utilisateur.query.get(int(user_id))

    @app.route('/')
    def accueil():
        produits_recents = Produit.query.filter_by(est_disponible=True).limit(4).all()
        return render_template('accueil.html', produits=produits_recents)

    # ============================================
    # ENREGISTRER LES BLUEPRINTS
    # ============================================
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    from app.controllers.profil_controller import profil_bp
    app.register_blueprint(profil_bp)

    from app.controllers.produit_controller import produit_bp
    app.register_blueprint(produit_bp)

    from app.controllers.panier_controller import panier_bp
    app.register_blueprint(panier_bp)

    from app.controllers.commande_controller import commande_bp
    app.register_blueprint(commande_bp)

    from app.controllers.admin_controller import admin_bp
    app.register_blueprint(admin_bp)

    from app.controllers.paiement_controller import paiement_bp
    app.register_blueprint(paiement_bp)

    from app.controllers.paypal_controller import paypal_bp
    app.register_blueprint(paypal_bp)

    from app.controllers.contact_controller import contact_bp
    app.register_blueprint(contact_bp)

    return app