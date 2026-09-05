"""Add performance indexes

Revision ID: 0a91be9bcddc
Revises: f904f939bbe8
Create Date: 2026-09-05 01:10:02.176643

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0a91be9bcddc'
down_revision = 'f904f939bbe8'
branch_labels = None
depends_on = None


def upgrade():
    # Index pour les produits
    op.create_index('ix_produits_est_disponible', 'produits', ['est_disponible'])
    op.create_index('ix_produits_categorie_id', 'produits', ['categorie_id'])
    op.create_index('ix_produits_est_service', 'produits', ['est_service'])
    op.create_index('ix_produits_date_creation', 'produits', ['date_creation'])
    op.create_index('ix_produits_slug', 'produits', ['slug'])

    # Index pour les commandes
    op.create_index('ix_commandes_statut', 'commandes', ['statut'])
    op.create_index('ix_commandes_utilisateur_id', 'commandes', ['utilisateur_id'])
    op.create_index('ix_commandes_date_creation', 'commandes', ['date_creation'])
    op.create_index('ix_commandes_reference', 'commandes', ['reference'])

    # Index pour les utilisateurs
    op.create_index('ix_utilisateurs_email', 'utilisateurs', ['email'])
    op.create_index('ix_utilisateurs_role', 'utilisateurs', ['role'])
    op.create_index('ix_utilisateurs_est_admin', 'utilisateurs', ['est_admin'])

    # Index pour les catégories
    op.create_index('ix_categories_slug', 'categories', ['slug'])

    # Index pour les lignes de commande
    op.create_index('ix_lignes_commandes_commande_id', 'lignes_commandes', ['commande_id'])
    op.create_index('ix_lignes_commandes_produit_id', 'lignes_commandes', ['produit_id'])


def downgrade():
    # Supprimer les index
    op.drop_index('ix_produits_est_disponible', table_name='produits')
    op.drop_index('ix_produits_categorie_id', table_name='produits')
    op.drop_index('ix_produits_est_service', table_name='produits')
    op.drop_index('ix_produits_date_creation', table_name='produits')
    op.drop_index('ix_produits_slug', table_name='produits')

    op.drop_index('ix_commandes_statut', table_name='commandes')
    op.drop_index('ix_commandes_utilisateur_id', table_name='commandes')
    op.drop_index('ix_commandes_date_creation', table_name='commandes')
    op.drop_index('ix_commandes_reference', table_name='commandes')

    op.drop_index('ix_utilisateurs_email', table_name='utilisateurs')
    op.drop_index('ix_utilisateurs_role', table_name='utilisateurs')
    op.drop_index('ix_utilisateurs_est_admin', table_name='utilisateurs')

    op.drop_index('ix_categories_slug', table_name='categories')

    op.drop_index('ix_lignes_commandes_commande_id', table_name='lignes_commandes')
    op.drop_index('ix_lignes_commandes_produit_id', table_name='lignes_commandes')