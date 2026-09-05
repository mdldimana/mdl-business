from flask import Blueprint, render_template, request, url_for
from app.models import Produit, Categorie

produit_bp = Blueprint('produit', __name__)

PRODUITS_PAR_PAGE = 12


@produit_bp.route('/produits')
def liste_produits():
    """Affiche la liste de tous les produits avec pagination"""
    page = request.args.get('page', 1, type=int)

    pagination = Produit.query.filter_by(est_disponible=True) \
        .order_by(Produit.id) \
        .paginate(page=page, per_page=PRODUITS_PAR_PAGE, error_out=False)

    produits = pagination.items
    categories = Categorie.query.filter_by(est_active=True).all()

    return render_template('produits/liste.html',
                           produits=produits,
                           categories=categories,
                           pagination=pagination)


@produit_bp.route('/produit/<slug>')
def detail_produit(slug):
    """Affiche le détail d'un produit"""
    produit = Produit.query.filter_by(slug=slug, est_disponible=True).first_or_404()
    return render_template('produits/detail.html', produit=produit)


@produit_bp.route('/categorie/<slug>')
def produits_par_categorie(slug):
    """Affiche les produits d'une catégorie avec pagination"""
    page = request.args.get('page', 1, type=int)

    categorie = Categorie.query.filter_by(slug=slug, est_active=True).first_or_404()

    pagination = Produit.query.filter_by(
        categorie_id=categorie.id,
        est_disponible=True
    ).order_by(Produit.id) \
        .paginate(page=page, per_page=PRODUITS_PAR_PAGE, error_out=False)

    produits = pagination.items
    categories = Categorie.query.filter_by(est_active=True).all()

    return render_template('produits/liste.html',
                           produits=produits,
                           categories=categories,
                           categorie_active=categorie,
                           pagination=pagination)


@produit_bp.route('/services')
def liste_services():
    """Affiche la liste des services"""
    services = Produit.query.filter_by(est_service=True, est_disponible=True).all()
    categories = Categorie.query.filter_by(est_active=True).all()

    return render_template('produits/services.html',
                           services=services,
                           categories=categories)


@produit_bp.route('/service/<slug>')
def detail_service(slug):
    """Affiche le détail d'un service"""
    service = Produit.query.filter_by(slug=slug, est_service=True, est_disponible=True).first_or_404()

    services_similaires = Produit.query.filter(
        Produit.est_service == True,
        Produit.id != service.id,
        Produit.est_disponible == True
    ).limit(3).all()

    return render_template('produits/detail_service.html',
                           service=service,
                           services_similaires=services_similaires)