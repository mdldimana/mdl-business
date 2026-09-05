from app import create_app, db
from app.models import Commande
from app.services.qrcode_service import generer_qr_code
import os

app = create_app()

with app.app_context():
    # Récupérer toutes les commandes sans QR Code
    commandes = Commande.query.filter(Commande.qr_code.is_(None)).all()

    print(f"🔍 {len(commandes)} commandes sans QR Code trouvées")

    for commande in commandes:
        try:
            qr_path = generer_qr_code(commande)
            commande.qr_code = qr_path
            db.session.commit()
            print(f"✅ QR Code généré pour {commande.reference}")
        except Exception as e:
            print(f"❌ Erreur pour {commande.reference}: {e}")

    print("🎉 Terminé !")