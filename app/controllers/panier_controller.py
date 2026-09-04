from flask import Blueprint, render_template, request, jsonify, session
from app.models import Produit

panier_bp = Blueprint('panier', __name__)


@panier_bp.route('/panier')
def voir_panier():
    """Affiche le contenu du panier"""
    panier = session.get('panier', {})
    produits = []
    total = 0

    for produit_id, quantite in panier.items():
        produit = Produit.query.get(int(produit_id))
        if produit:
            sous_total = produit.prix_actuel * quantite
            total += sous_total
            produits.append({
                'produit': produit,
                'quantite': quantite,
                'sous_total': sous_total
            })

    return render_template('panier/panier.html',
                           produits=produits,
                           total=total)


@panier_bp.route('/api/panier/total', methods=['GET'])
def total_panier():
    """Retourne le nombre total d'articles dans le panier"""
    panier = session.get('panier', {})
    total_articles = sum(panier.values()) if panier else 0
    return jsonify({'total': total_articles})


@panier_bp.route('/api/panier/ajouter', methods=['POST'])
def ajouter_panier():
    """Ajoute un produit au panier (AJAX)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données invalides'})

        produit_id = str(data.get('produit_id'))
        quantite = int(data.get('quantite', 1))

        # Vérifier que le produit existe
        produit = Produit.query.get(int(produit_id))
        if not produit:
            return jsonify({'success': False, 'message': 'Produit introuvable'})

        if not produit.en_stock:
            return jsonify({'success': False, 'message': 'Produit indisponible'})

        # Récupérer ou créer le panier
        panier = session.get('panier', {})

        if produit_id in panier:
            panier[produit_id] += quantite
        else:
            panier[produit_id] = quantite

        session['panier'] = panier
        session.modified = True

        total_articles = sum(panier.values())
        return jsonify({
            'success': True,
            'message': f'{produit.nom} ajouté au panier',
            'total_articles': total_articles
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@panier_bp.route('/api/panier/supprimer', methods=['POST'])
def supprimer_panier():
    """Supprime un produit du panier"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données invalides'})

        produit_id = str(data.get('produit_id'))

        panier = session.get('panier', {})
        if produit_id in panier:
            del panier[produit_id]
            session['panier'] = panier
            session.modified = True

        total_articles = sum(panier.values())
        return jsonify({
            'success': True,
            'total_articles': total_articles
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@panier_bp.route('/api/panier/vider', methods=['POST'])
def vider_panier():
    """Vide le panier"""
    session.pop('panier', None)
    session.modified = True
    return jsonify({'success': True})


@panier_bp.route('/api/panier/quantite', methods=['POST'])
def modifier_quantite():
    """Modifie la quantité d'un produit"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données invalides'})

        produit_id = str(data.get('produit_id'))
        quantite = int(data.get('quantite', 0))

        panier = session.get('panier', {})

        if quantite <= 0:
            if produit_id in panier:
                del panier[produit_id]
        else:
            panier[produit_id] = quantite

        session['panier'] = panier
        session.modified = True

        total_articles = sum(panier.values())
        return jsonify({
            'success': True,
            'total_articles': total_articles
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})