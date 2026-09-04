from app import create_app, db
from app.models import Produit, Categorie
from datetime import datetime

app = create_app()

with app.app_context():
    # Récupérer la catégorie Services
    categorie = Categorie.query.filter_by(slug='services').first()

    if not categorie:
        print("❌ Catégorie 'Services' non trouvée. Créez-la d'abord.")
        exit()

    # Supprimer les anciens services
    Produit.query.filter_by(est_service=True).delete()
    db.session.commit()

    print("📦 Création des services...")

    services = [
        {
            'nom': 'PhotoBooth Professionnel',
            'slug': 'photobooth-pro',
            'description': """Service PhotoBooth haut de gamme pour vos événements. 
            Cabine photo automatique avec accessoires, impressions instantanées et galerie en ligne.
            Idéal pour : mariages, anniversaires, soirées d'entreprise.""",
            'prix': 350.00,
            'stock': 999,
            'est_service': True,
            'duree': '4 heures',
            'livrable': False,
            'garantie': 'Satisfait ou remboursé',
            'caracteristiques': 'Impressions instantanées, Accessoires variés, Galerie en ligne, Personnalisation des photos'
        },
        {
            'nom': 'Création de Sites Web',
            'slug': 'creation-site-web',
            'description': """Création de sites internet professionnels sur mesure.
            Design responsive, optimisation SEO, intégration e-commerce, et formation à l'administration.
            Technologies : HTML5, CSS3, JavaScript, Python, Flask, React.""",
            'prix': 1500.00,
            'stock': 999,
            'est_service': True,
            'duree': '2 semaines',
            'livrable': True,
            'garantie': 'Garantie 6 mois',
            'caracteristiques': 'Design responsive, Optimisation SEO, E-commerce intégré, Administration facile, Formation incluse'
        },
        {
            'nom': 'Photographie Événementielle',
            'slug': 'photographie-evenementielle',
            'description': """Reportage photo professionnel pour tous vos événements.
            Mariages, baptêmes, anniversaires, séances en entreprise.
            Livraison : galerie en ligne + clé USB + album photo.""",
            'prix': 400.00,
            'stock': 999,
            'est_service': True,
            'duree': '6 heures',
            'livrable': False,
            'garantie': 'Satisfait ou remboursé',
            'caracteristiques': 'Galerie en ligne, Album photo inclus, Clé USB offerte, Tirage haut de gamme'
        },
        {
            'nom': 'Achat sur Alibaba',
            'slug': 'achat-alibaba',
            'description': """Service de sourcing et achat sur Alibaba.
            Nous vous aidons à trouver les meilleurs fournisseurs, négocier les prix, 
            et gérer la logistique d'importation.
            Service clé en main pour les entrepreneurs.""",
            'prix': 250.00,
            'stock': 999,
            'est_service': True,
            'duree': '1 mois',
            'livrable': True,
            'garantie': 'Qualité vérifiée',
            'caracteristiques': 'Sourcing fournisseurs, Négociation des prix, Logistique import, Contrôle qualité, Suivi personnalisé'
        },
        {
            'nom': 'Montage Vidéo Professionnel',
            'slug': 'montage-video-pro',
            'description': """Service de montage vidéo professionnel pour vos projets.
            Montage, étalonnage, effets spéciaux, sous-titrage, et optimisation pour les réseaux sociaux.
            Formats : YouTube, Instagram, TikTok, sites web.""",
            'prix': 180.00,
            'stock': 999,
            'est_service': True,
            'duree': '3 jours',
            'livrable': True,
            'garantie': 'Garantie 1 mois',
            'caracteristiques': 'Montage HD, Effets spéciaux, Sous-titrage, Optimisation réseaux sociaux, Sons et musique'
        },
        {
            'nom': 'Marketing Digital - Consulting',
            'slug': 'marketing-digital',
            'description': """Consulting en marketing digital pour développer votre présence en ligne.
            Stratégie social media, campagnes publicitaires, SEO, email marketing et analytics.
            Un plan d'action personnalisé pour atteindre vos objectifs.""",
            'prix': 800.00,
            'stock': 999,
            'est_service': True,
            'duree': '3 semaines',
            'livrable': True,
            'garantie': 'Stratégie garantie',
            'caracteristiques': 'Stratégie social media, Campagnes publicitaires, SEO, Email marketing, Analytics'
        }
    ]

    for s in services:
        service = Produit(
            nom=s['nom'],
            slug=s['slug'],
            description=s['description'],
            prix=s['prix'],
            stock=s['stock'],
            categorie_id=categorie.id,
            est_service=True,
            est_disponible=True,
            duree=s['duree'],
            livrable=s['livrable'],
            garantie=s['garantie'],
            caracteristiques=s['caracteristiques']
        )
        db.session.add(service)

    db.session.commit()
    print(f"✅ {len(services)} services créés avec succès !")