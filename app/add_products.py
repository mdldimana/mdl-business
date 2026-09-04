from app import create_app, db
from app.models import Categorie, Produit
from datetime import datetime

app = create_app()

with app.app_context():
    # Supprimer les anciennes données (optionnel)
    print("🗑️  Suppression des anciens produits...")
    Produit.query.delete()
    Categorie.query.delete()
    db.session.commit()

    # Créer les catégories
    print("📁 Création des catégories...")
    categories = [
        Categorie(nom='Montres', slug='montres', description='Montres de luxe et sportives'),
        Categorie(nom='Accessoires', slug='accessoires', description='Accessoires pour hommes et femmes'),
        Categorie(nom='Électronique', slug='electronique', description='Appareils électroniques high-tech'),
        Categorie(nom='Services', slug='services', description='Services professionnels')
    ]

    for cat in categories:
        db.session.add(cat)

    db.session.commit()
    print("✅ Catégories créées avec succès !")

    # Récupérer les catégories
    montres = Categorie.query.filter_by(slug='montres').first()
    accessoires = Categorie.query.filter_by(slug='accessoires').first()
    electronique = Categorie.query.filter_by(slug='electronique').first()
    services = Categorie.query.filter_by(slug='services').first()

    # Créer les produits
    print("📦 Création des produits...")
    produits = [
        Produit(
            nom='Montre Rolex Submariner',
            slug='rolex-submariner',
            description='Montre de luxe automatique, étanche 300m, boîtier acier 904L.',
            prix=8500.00,
            stock=5,
            categorie_id=montres.id,
            est_disponible=True
        ),
        Produit(
            nom='Montre Apple Watch Ultra',
            slug='apple-watch-ultra',
            description='Montre connectée avec GPS, écran toujours allumé, résistance à l\'eau.',
            prix=899.00,
            prix_promo=799.00,
            stock=15,
            categorie_id=montres.id,
            est_disponible=True
        ),
        Produit(
            nom='Sac à dos Cuir Vintage',
            slug='sac-cuir-vintage',
            description='Sac à dos en cuir véritable, fabriqué à la main, style vintage.',
            prix=120.00,
            stock=20,
            categorie_id=accessoires.id,
            est_disponible=True
        ),
        Produit(
            nom='Portefeuille Homme Cuir',
            slug='portefeuille-cuir-homme',
            description='Portefeuille en cuir de vachette, 6 emplacements pour cartes.',
            prix=45.00,
            prix_promo=35.00,
            stock=30,
            categorie_id=accessoires.id,
            est_disponible=True
        ),
        Produit(
            nom='Casque Audio Sony WH-1000XM5',
            slug='sony-wh-1000xm5',
            description='Casque Bluetooth avec réduction de bruit active, autonomie 30h.',
            prix=399.00,
            stock=10,
            categorie_id=electronique.id,
            est_disponible=True
        ),
        Produit(
            nom='Enceinte JBL Charge 5',
            slug='jbl-charge-5',
            description='Enceinte Bluetooth portable, étanche IP67, autonomie 20h.',
            prix=149.00,
            prix_promo=129.00,
            stock=25,
            categorie_id=electronique.id,
            est_disponible=True
        ),
        Produit(
            nom='Photographie Professionnelle',
            slug='photographie-pro',
            description='Séance photo professionnelle pour événements, mariages, portraits.',
            prix=250.00,
            stock=999,
            categorie_id=services.id,
            est_disponible=True
        ),
        Produit(
            nom='Création de Site Web',
            slug='creation-site-web',
            description='Création de site internet professionnel sur mesure.',
            prix=1500.00,
            stock=999,
            categorie_id=services.id,
            est_disponible=True
        )
    ]

    for p in produits:
        db.session.add(p)

    db.session.commit()
    print("✅ Produits créés avec succès !")

    # Afficher le résumé
    print("\n📊 RÉSUMÉ :")
    print(f"   Catégories : {Categorie.query.count()}")
    print(f"   Produits : {Produit.query.count()}")
    print("\n   🏷️  Connectez-vous avec admin@mdlbusiness.com / admin123")