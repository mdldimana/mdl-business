from app.extensions import db
from flask_login import UserMixin
from datetime import datetime


# ============================================
# MODÈLE UTILISATEUR
# ============================================
class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(128), nullable=False)
    prenom = db.Column(db.String(50))
    nom = db.Column(db.String(50))
    est_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='client')  # client, manager, comptable, admin
    est_actif = db.Column(db.Boolean, default=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    date_derniere_connexion = db.Column(db.DateTime)

    # Relations
    commandes = db.relationship('Commande', backref='client', lazy=True)

    def __repr__(self):
        return f"<Utilisateur {self.email}>"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}".strip() or self.email

# ============================================
# MODÈLE CATÉGORIE
# ============================================
class Categorie(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.Text)
    est_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    produits = db.relationship('Produit', backref='categorie', lazy=True)

    def __repr__(self):
        return f"<Categorie {self.nom}>"


# ============================================
# MODÈLE PRODUIT
# ============================================
class Produit(db.Model):
    __tablename__ = 'produits'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    prix = db.Column(db.Float, nullable=False)
    prix_promo = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    est_disponible = db.Column(db.Boolean, default=True)
    image_principale = db.Column(db.String(255))
    qr_code = db.Column(db.String(255))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # NOUVEAUX CHAMPS POUR LES SERVICES
    est_service = db.Column(db.Boolean, default=False)  # True pour les services
    duree = db.Column(db.String(50))  # Ex: "1 heure", "2 jours"
    livrable = db.Column(db.Boolean, default=True)  # Service livrable à distance ou non
    garantie = db.Column(db.String(100))  # Ex: "Garantie 1 an"
    caracteristiques = db.Column(db.Text)  # Liste des caractéristiques (format JSON ou texte)

    categorie_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # Relations
    lignes_commande = db.relationship('LigneCommande', backref='produit_ref', lazy=True)

    def __repr__(self):
        return f"<Produit {self.nom}>"

    @property
    def prix_actuel(self):
        return self.prix_promo if self.prix_promo and self.prix_promo < self.prix else self.prix

    @property
    def en_stock(self):
        return self.stock > 0

# ============================================
# MODÈLE COMMANDE
# ============================================
class Commande(db.Model):
    __tablename__ = 'commandes'

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)

    # Informations client
    email = db.Column(db.String(120), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20))

    # Adresses
    adresse_livraison = db.Column(db.Text, nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    code_postal = db.Column(db.String(10), nullable=False)
    pays = db.Column(db.String(50), nullable=False, default='France')

    # Montants
    sous_total = db.Column(db.Float, nullable=False)
    frais_livraison = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)

    # Statut
    statut = db.Column(db.String(30), default='en_attente')

    # Paiement
    mode_paiement = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    stripe_session_id = db.Column(db.String(100))

    # QR Code
    qr_code = db.Column(db.String(255))

    # Dates
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_mise_a_jour = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation avec l'utilisateur (déjà définie dans Utilisateur)
    utilisateur = db.relationship('Utilisateur', backref='commandes_utilisateur', lazy=True)

    # Relation avec les lignes de commande
    lignes = db.relationship('LigneCommande', backref='commande', lazy=True, cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Commande, self).__init__(*args, **kwargs)
        if not self.reference:
            self.reference = self.generer_reference()

    def generer_reference(self):
        """Génère une référence unique pour la commande"""
        import random
        import string
        prefix = "MDL"
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{timestamp}-{random_part}"

    def __repr__(self):
        return f"<Commande {self.reference}>"


# ============================================
# MODÈLE LIGNE DE COMMANDE
# ============================================
class LigneCommande(db.Model):
    __tablename__ = 'lignes_commandes'

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)

    # Copie des données du produit au moment de la commande
    nom_produit = db.Column(db.String(100), nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<LigneCommande {self.nom_produit} x{self.quantite}>"