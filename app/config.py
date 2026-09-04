import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # Utiliser DATABASE_URL en priorité (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Si DATABASE_URL n'est pas défini, utiliser les variables individuelles
    if not SQLALCHEMY_DATABASE_URI:
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_pass = os.environ.get('DB_PASS', '')
        db_name = os.environ.get('DB_NAME', 'ecommerce')
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False