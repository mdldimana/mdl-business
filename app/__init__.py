from flask import Flask, render_template
import os
from dotenv import load_dotenv

from app.extensions import db, migrate, bcrypt, login_manager
from app.models import Utilisateur, Categorie, Produit

load_dotenv()


def create_app():
    app = Flask(__name__,
                template_folder='views/templates',
                static_folder='views/static')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # ============================================ -->
    # UTILISER DATABASE_URL (POSTGRESQL)
    # ============================================ -->
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    # psycopg v3 utilise automatiquement postgresql+psycopg

    # Fallback pour le développement local
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}"
            f"@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}"
            f"/{os.environ.get('DB_NAME')}"
        )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Utilisateur.query.get(int(user_id))

    @app.route('/')
    def accueil():
        produits_recents = Produit.query.filter_by(est_disponible=True).limit(4).all()
        return render_template('accueil.html', produits=produits_recents)

    # Enregistrer les blueprints
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

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

    return app