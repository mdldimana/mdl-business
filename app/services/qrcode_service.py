import qrcode
import os
import cloudinary
import cloudinary.uploader
from flask import url_for
from datetime import datetime
import io


def generer_qr_code(commande):
    """
    Génère un QR Code pour une commande et le sauvegarde sur Cloudinary
    """
    # URL de suivi
    base_url = os.environ.get('BASE_URL', '')
    if base_url:
        url = f"{base_url}/commande/suivi/{commande.reference}"
    else:
        url = url_for('commande.suivi', reference=commande.reference, _external=True)

    print(f"🔗 URL de suivi: {url}")

    # Génération du QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Création de l'image
    img = qr.make_image(fill_color="black", back_color="white")

    # Sauvegarder temporairement en mémoire
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Upload vers Cloudinary
    try:
        result = cloudinary.uploader.upload(
            buffer,
            folder="mdl-business/qrcodes",
            public_id=f"commande_{commande.reference}",
            overwrite=True
        )
        cloudinary_url = result['secure_url']
        print(f"✅ QR Code uploadé sur Cloudinary: {cloudinary_url}")
        return cloudinary_url
    except Exception as e:
        print(f"❌ Erreur upload QR Code sur Cloudinary: {e}")
        # Fallback: sauvegarde locale
        qr_dir = os.path.join('app', 'views', 'static', 'images', 'qrcodes')
        os.makedirs(qr_dir, exist_ok=True)
        filename = f"commande_{commande.reference}.png"
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath)
        return f"images/qrcodes/{filename}"