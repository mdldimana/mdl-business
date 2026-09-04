import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

# Extensions autorisées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(file, subfolder='produits'):
    """
    Sauvegarde une image et retourne le chemin relatif.
    """
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        raise ValueError('Format de fichier non supporté. Utilisez JPG, PNG, GIF ou WEBP.')

    # Générer un nom unique
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Chemin de sauvegarde
    upload_dir = os.path.join('app', 'views', 'static', 'images', subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Retourner le chemin relatif pour la base de données
    return f"images/{subfolder}/{filename}"