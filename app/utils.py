import cloudinary
import cloudinary.uploader
import os

# Configurer Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)


def upload_image(file, subfolder='produits'):
    """Upload une image sur Cloudinary"""
    if not file or file.filename == '':
        return None

    # Vérifier les extensions autorisées
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError('Format de fichier non supporté.')

    try:
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=f"mdl-business/{subfolder}",
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto'},
                {'fetch_format': 'auto'}
            ]
        )
        return result['secure_url']  # URL permanente
    except Exception as e:
        print(f"❌ Erreur upload Cloudinary: {e}")
        return None