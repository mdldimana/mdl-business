import qrcode
import os
from flask import url_for
from datetime import datetime


def generer_qr_code(commande):
    """
    Génère un QR Code pour une commande et le sauvegarde
    """
    # Dossier de stockage
    qr_dir = os.path.join('app', 'views', 'static', 'images', 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)

    # Nom du fichier
    filename = f"commande_{commande.reference}.png"
    filepath = os.path.join(qr_dir, filename)

    # URL de suivi
    url = url_for('commande.suivi', reference=commande.reference, _external=True)

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
    img.save(filepath)

    # Retourner le chemin relatif
    return f"images/qrcodes/{filename}"


def generer_qr_code_produit(produit):
    """
    Génère un QR Code pour un produit
    """
    qr_dir = os.path.join('app', 'views', 'static', 'images', 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)

    filename = f"produit_{produit.slug}.png"
    filepath = os.path.join(qr_dir, filename)

    url = url_for('produit.detail_produit', slug=produit.slug, _external=True)

    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)

    return f"images/qrcodes/{filename}"