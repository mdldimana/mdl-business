"""Ajout du champ telephone dans utilisateurs

Revision ID: 93bb5b0297b7
Revises: 0a91be9bcddc
Create Date: 2026-09-05 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93bb5b0297b7'
down_revision = '0a91be9bcddc'
branch_labels = None
depends_on = None


def upgrade():
    # AJOUTER LA COLONNE TELEPHONE DANS UTILISATEURS
    op.add_column('utilisateurs', sa.Column('telephone', sa.String(length=20), nullable=True))


def downgrade():
    # SUPPRIMER LA COLONNE TELEPHONE
    op.drop_column('utilisateurs', 'telephone')g