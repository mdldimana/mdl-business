from app import create_app, db
from app.models import Utilisateur, Categorie, Produit
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
app = create_app()

with app.app_context():
    print("🔄 Début du peuplement de la base de données...")

    # ============================================
    # 1. CRÉER L'ADMIN
    # ============================================
    if not Utilisateur.query.filter_by(email='admin@mdlbusiness.com').first():
        admin = Utilisateur(
            email='admin@mdlbusiness.com',
            prenom='Admin',
            nom='MDL',
            est_admin=True,
            est_actif=True,
            role='admin',
            mot_de_passe_hash=bcrypt.generate_password_hash('admin123').decode('utf-8')
        )
        db.session.add(admin)
        print("✅ Admin créé")
    else:
        print("ℹ️ Admin existe déjà")

    # ============================================
    # 2. CRÉER LES CATÉGORIES
    # ============================================
    categories = [
        {'nom': 'Montres', 'slug': 'montres', 'description': 'Montres de luxe et sportives'},
        {'nom': 'Accessoires', 'slug': 'accessoires', 'description': 'Accessoires pour hommes et femmes'},
        {'nom': 'Électronique', 'slug': 'electronique', 'description': 'Appareils électroniques high-tech'},
        {'nom': 'Services', 'slug': 'services', 'description': 'Services professionnels'}
    ]

    for cat_data in categories:
        if not Categorie.query.filter_by(slug=cat_data['slug']).first():
            cat = Categorie(**cat_data)
            db.session.add(cat)
            print(f"✅ Catégorie {cat_data['nom']} créée")
        else:
            print(f"ℹ️ Catégorie {cat_data['nom']} existe déjà")

    db.session.commit()

    # ============================================
    # 3. RÉCUPÉRER LES CATÉGORIES POUR LES PRODUITS
    # ============================================
    montres = Categorie.query.filter_by(slug='montres').first()
    accessoires = Categorie.query.filter_by(slug='accessoires').first()
    electronique = Categorie.query.filter_by(slug='electronique').first()
    services = Categorie.query.filter_by(slug='services').first()

    # ============================================
    # 4. CRÉER LES PRODUITS
    # ============================================
    produits = [
        # Montres
        {
            'nom': 'Montre Rolex Submariner',
            'slug': 'rolex-submariner',
            'description': 'Montre de luxe automatique, étanche 300m, boîtier acier 904L.',
            'prix': 9500.00,
            'stock': 5,
            'categorie': montres,
            'est_disponible': True
        },
        {
            'nom': 'Montre Apple Watch Ultra',
            'slug': 'apple-watch-ultra',
            'description': 'Montre connectée avec GPS, écran toujours allumé, résistance à l\'eau.',
            'prix': 899.00,
            'prix_promo': 799.00,
            'stock': 15,
            'categorie': montres,
            'est_disponible': True
        },
        # Accessoires
        {
            'nom': 'Sac à dos Cuir Vintage',
            'slug': 'sac-cuir-vintage',
            'description': 'Sac à dos en cuir véritable, fabriqué à la main, style vintage.',
            'prix': 120.00,
            'stock': 20,
            'categorie': accessoires,
            'est_disponible': True
        },
        {
            'nom': 'Portefeuille Homme Cuir',
            'slug': 'portefeuille-cuir-homme',
            'description': 'Portefeuille en cuir de vachette, 6 emplacements pour cartes.',
            'prix': 45.00,
            'prix_promo': 35.00,
            'stock': 30,
            'categorie': accessoires,
            'est_disponible': True
        },
        # Électronique
        {
            'nom': 'Casque Audio Sony WH-1000XM5',
            'slug': 'sony-wh-1000xm5',
            'description': 'Casque Bluetooth avec réduction de bruit active, autonomie 30h.',
            'prix': 399.00,
            'stock': 10,
            'categorie': electronique,
            'est_disponible': True
        },
        {
            'nom': 'Enceinte JBL Charge 5',
            'slug': 'jbl-charge-5',
            'description': 'Enceinte Bluetooth portable, étanche IP67, autonomie 20h.',
            'prix': 149.00,
            'prix_promo': 129.00,
            'stock': 25,
            'categorie': electronique,
            'est_disponible': True
        },
        # Services
        {
            'nom': 'Photographie Professionnelle',
            'slug': 'photographie-pro',
            'description': 'Séance photo professionnelle pour événements, mariages, portraits.',
            'prix': 250.00,
            'stock': 999,
            'categorie': services,
            'est_disponible': True,
            'est_service': True,
            'duree': '4 heures',
            'livrable': False,
            'garantie': 'Satisfait ou remboursé'
        },
        {
            'nom': 'Création de Site Web',
            'slug': 'creation-site-web',
            'description': 'Création de site internet professionnel sur mesure.',
            'prix': 1500.00,
            'stock': 999,
            'categorie': services,
            'est_disponible': True,
            'est_service': True,
            'duree': '2 semaines',
            'livrable': True,
            'garantie': 'Garantie 6 mois'
        }
    ]

    for p in produits:
        # Vérifier si le produit existe déjà
        if not Produit.query.filter_by(slug=p['slug']).first():
            produit = Produit(
                nom=p['nom'],
                slug=p['slug'],
                description=p['description'],
                prix=p['prix'],
                prix_promo=p.get('prix_promo'),
                stock=p['stock'],
                categorie_id=p['categorie'].id,
                est_disponible=p['est_disponible'],
                est_service=p.get('est_service', False),
                duree=p.get('duree'),
                livrable=p.get('livrable', True),
                garantie=p.get('garantie')
            )
            db.session.add(produit)
            print(f"✅ Produit {p['nom']} créé")
        else:
            print(f"ℹ️ Produit {p['nom']} existe déjà")

    db.session.commit()
    print("🎉 Peuplement terminé !")