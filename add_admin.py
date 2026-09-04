from app import create_app, db
from app.models import Utilisateur
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
app = create_app()

with app.app_context():
    # Vérifier si l'admin existe déjà
    admin = Utilisateur.query.filter_by(email='admin@mdlbusiness.com').first()

    if not admin:
        admin = Utilisateur(
            email='admin@mdlbusiness.com',
            prenom='Admin',
            nom='MDL',
            est_admin=True,
            est_actif=True,
            mot_de_passe_hash=bcrypt.generate_password_hash('admin123').decode('utf-8')
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Administrateur créé avec succès !")
        print("   Email: admin@mdlbusiness.com")
        print("   Mot de passe: admin123")
    else:
        print("ℹ️ L'administrateur existe déjà.")