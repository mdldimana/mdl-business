import os
from datetime import datetime
from flask import url_for, current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


class PDFService:
    """Service de génération de PDF pour les commandes avec ReportLab"""

    @staticmethod
    def _trouver_logo():
        """Trouve le logo dans les différents chemins possibles"""
        base_dir = os.getcwd()
        possible_paths = [
            os.path.join(base_dir, 'app', 'views', 'static', 'images', 'logos', 'logo.png'),
            os.path.join(base_dir, 'app', 'views', 'static', 'images', 'logos', 'logo.jpg'),
            os.path.join(base_dir, 'app', 'static', 'images', 'logos', 'logo.png'),
            os.path.join('app', 'views', 'static', 'images', 'logos', 'logo.png'),
            os.path.join('static', 'images', 'logos', 'logo.png'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    @staticmethod
    def _ajouter_logo_et_titre(story, titre, sous_titre=""):
        """
        Ajoute le logo et le titre à un PDF
        """
        styles = getSampleStyleSheet()

        style_title = ParagraphStyle('Title', parent=styles['Title'],
                                     fontSize=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
        style_subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                        alignment=TA_CENTER, fontSize=10, textColor=colors.HexColor('#6c757d'))

        # Logo
        logo_path = PDFService._trouver_logo()

        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=1.8 * inch, height=0.9 * inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 5))
            except Exception as e:
                print(f"⚠️ Erreur chargement logo: {e}")

        # Titre
        story.append(Paragraph(titre, style_title))
        if sous_titre:
            story.append(Paragraph(sous_titre, style_subtitle))

        story.append(Paragraph(f"MDL Business - {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                               ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)))
        story.append(Spacer(1, 20))

    @staticmethod
    def generer_facture(commande):
        """
        Génère une facture PDF avec un design moderne et professionnel
        """
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=60, leftMargin=60,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()

        # ============================================
        # COULEURS
        # ============================================
        COLOR_PRIMARY = colors.HexColor('#0f172a')
        COLOR_SECONDARY = colors.HexColor('#1e293b')
        COLOR_ACCENT = colors.HexColor('#3b82f6')
        COLOR_ACCENT_DARK = colors.HexColor('#2563eb')
        COLOR_SUCCESS = colors.HexColor('#22c55e')
        COLOR_WARNING = colors.HexColor('#f59e0b')
        COLOR_LIGHT_BG = colors.HexColor('#f8fafc')
        COLOR_BORDER = colors.HexColor('#e2e8f0')
        COLOR_TEXT_MUTED = colors.HexColor('#64748b')
        COLOR_WHITE = colors.white

        # ============================================
        # STYLES PERSONNALISÉS
        # ============================================
        style_title = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontSize=24,
            textColor=COLOR_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        )

        style_subtitle = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_CENTER,
            spaceAfter=15
        )

        style_section_title = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=COLOR_PRIMARY,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )

        style_label = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=8,
            textColor=COLOR_TEXT_MUTED,
            fontName='Helvetica',
            spaceAfter=1
        )

        style_value = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLOR_PRIMARY,
            fontName='Helvetica-Bold'
        )

        style_footer = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_CENTER
        )

        style_status = ParagraphStyle(
            'Status',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold'
        )

        # ============================================
        # ÉLÉMENTS DU PDF
        # ============================================
        story = []

        # ============================================
        # EN-TÊTE - DESIGN MODERNE
        # ============================================
        # Logo et titre
        logo_path = PDFService._trouver_logo()

        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=1.8 * inch, height=0.9 * inch)
                logo.hAlign = 'CENTER'

                header_data = [
                    [logo,
                     Paragraph(
                         "<b>MDL BUSINESS</b><br/><font size='9' color='#64748b'>Facture de commande</font>",
                         ParagraphStyle('HeaderText', parent=styles['Normal'],
                                        alignment=TA_CENTER, fontSize=16,
                                        textColor=COLOR_PRIMARY))]
                ]
                header_table = Table(header_data, colWidths=[1.8 * inch, 3.5 * inch])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (0, 0), 0),
                    ('RIGHTPADDING', (1, 0), (1, 0), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(header_table)
            except Exception as e:
                print(f"⚠️ Erreur chargement logo: {e}")
                story.append(Paragraph("MDL BUSINESS", style_title))
                story.append(Paragraph("Facture de commande", style_subtitle))
        else:
            story.append(Paragraph("MDL BUSINESS", style_title))
            story.append(Paragraph("Facture de commande", style_subtitle))

        story.append(Spacer(1, 5))

        # Référence et statut
        status_color = COLOR_SUCCESS if commande.statut == 'livree' else COLOR_WARNING if commande.statut == 'en_attente' else COLOR_ACCENT
        status_text = commande.statut.replace('_', ' ').title()

        ref_data = [
            [Paragraph(f"Référence: <b>#{commande.reference}</b>", style_value),
             Paragraph(f"<b>Statut:</b> <font color='{status_color.hexval()}'>{status_text}</font>", style_status)],
            [Paragraph(f"Date: {commande.date_creation.strftime('%d/%m/%Y à %H:%M')}", styles['Normal']),
             Paragraph(f"Paiement: {commande.mode_paiement or 'Non spécifié'}", styles['Normal'])]
        ]

        ref_table = Table(ref_data, colWidths=[3 * inch, 2.5 * inch])
        ref_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(ref_table)

        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER))
        story.append(Spacer(1, 12))

        # ============================================
        # INFOS CLIENT ET LIVRAISON
        # ============================================
        header_info_data = [
            [
                Paragraph("<b>👤 Informations client</b>", style_section_title),
                Paragraph("<b>📍 Adresse de livraison</b>", style_section_title)
            ]
        ]
        header_info_table = Table(header_info_data, colWidths=[3 * inch, 3 * inch])
        header_info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(header_info_table)

        info_data = [
            [
                Paragraph(
                    f"<b>{commande.prenom} {commande.nom}</b><br/>{commande.email}<br/>{'Tél: ' + commande.telephone if commande.telephone else 'Tél: Non renseigné'}",
                    styles['Normal']),
                Paragraph(
                    f"{commande.adresse_livraison.replace(chr(10), '<br/>')}<br/>{commande.code_postal} {commande.ville}<br/>{commande.pays}",
                    styles['Normal'])
            ]
        ]

        info_table = Table(info_data, colWidths=[3 * inch, 3 * inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(info_table)

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 10))

        # ============================================
        # TABLEAU DES ARTICLES
        # ============================================
        story.append(Paragraph("📦 Détail des articles", style_section_title))
        story.append(Spacer(1, 6))

        data = [
            ['#', 'Produit', 'Qté', 'Prix unit.', 'Total']
        ]

        total_articles = 0
        for i, ligne in enumerate(commande.lignes, 1):
            data.append([
                str(i),
                ligne.nom_produit,
                str(ligne.quantite),
                f"{ligne.prix_unitaire:.2f} $",
                f"{ligne.prix_unitaire * ligne.quantite:.2f} $"
            ])
            total_articles += ligne.quantite

        table = Table(data, colWidths=[0.4 * inch, 2.8 * inch, 0.6 * inch, 1.2 * inch, 1.4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_WHITE),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
            ('TOPPADDING', (0, 1), (-1, -2), 6),
            ('BACKGROUND', (0, 1), (-1, -2), COLOR_LIGHT_BG),
            ('BACKGROUND', (0, 2), (-1, -2), COLOR_WHITE),
            ('GRID', (0, 0), (-1, -2), 0.5, COLOR_BORDER),
            ('LINEABOVE', (0, -1), (-1, -1), 2, COLOR_PRIMARY),
            ('BACKGROUND', (0, -1), (-1, -1), COLOR_LIGHT_BG),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, -1), (1, -1), 'CENTER'),
            ('ALIGN', (2, -1), (4, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, -1), (-1, -1), COLOR_ACCENT),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
        ]))

        story.append(table)

        story.append(Spacer(1, 15))

        # ============================================
        # RÉSUMÉ DES TOTAUX
        # ============================================
        sous_total = commande.sous_total or commande.total
        frais_livraison = commande.frais_livraison or 0

        totals_data = [
            ['Sous-total', f"{sous_total:.2f} $"],
            ['Frais de livraison', f"{frais_livraison:.2f} $"],
        ]

        totals_data.append(['TOTAL', f"{commande.total:.2f} $"])

        totals_table = Table(totals_data, colWidths=[2.5 * inch, 1.5 * inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (0, -2), 9),
            ('FONTSIZE', (1, 0), (1, -2), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -2), 4),
            ('TOPPADDING', (0, 0), (-1, -2), 4),
            ('LINEABOVE', (0, -1), (-1, -1), 2, COLOR_PRIMARY),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (1, -1), COLOR_ACCENT),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ('TOPPADDING', (0, -1), (-1, -1), 8),
            ('BACKGROUND', (0, -1), (-1, -1), COLOR_LIGHT_BG),
        ]))

        story.append(totals_table)

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 15))

        # ============================================
        # MESSAGE DE REMERCIEMENT
        # ============================================
        thanks_style = ParagraphStyle(
            'Thanks',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            textColor=COLOR_PRIMARY,
            fontName='Helvetica-Bold',
            spaceAfter=4
        )

        story.append(Paragraph("🙏 Merci pour votre confiance !", thanks_style))

        if commande.transaction_id:
            story.append(Paragraph(f"Transaction: {commande.transaction_id}", style_footer))

        story.append(Spacer(1, 15))

        # ============================================
        # PIED DE PAGE
        # ============================================
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_CENTER
        )

        story.append(HRFlowable(width="50%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 5))

        story.append(Paragraph("MDL Business - Tous droits réservés", footer_style))
        story.append(Paragraph(f"Facture générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", footer_style))
        story.append(Paragraph("www.mdl-business.com - contact@mdl-business.com", footer_style))

        # ============================================
        # CONSTRUIRE LE PDF
        # ============================================
        doc.build(story)

        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    @staticmethod
    def sauvegarder_facture(commande, dossier='factures'):
        """
        Sauvegarde la facture PDF sur le serveur
        """
        facture_dir = os.path.join('app', 'views', 'static', dossier)
        os.makedirs(facture_dir, exist_ok=True)

        filename = f"facture_{commande.reference}.pdf"
        filepath = os.path.join(facture_dir, filename)

        pdf = PDFService.generer_facture(commande)

        with open(filepath, 'wb') as f:
            f.write(pdf)

        return f"{dossier}/{filename}"

    @staticmethod
    def generer_catalogue_produits(produits):
        """Génère un catalogue PDF de tous les produits"""
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=60, leftMargin=60,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()
        story = []

        # ============================================
        # LOGO ET TITRE
        # ============================================
        PDFService._ajouter_logo_et_titre(story, "Catalogue des produits")

        # Tableau des produits
        data = [['#', 'Nom', 'Catégorie', 'Prix', 'Stock', 'Statut']]

        for i, p in enumerate(produits, 1):
            data.append([
                str(i),
                p.nom,
                p.categorie.nom if p.categorie else '-',
                f"{p.prix_actuel:.2f} $",
                str(p.stock),
                'Disponible' if p.est_disponible else 'Indisponible'
            ])

        table = Table(data, colWidths=[0.5 * inch, 2.5 * inch, 1.5 * inch, 1 * inch, 0.8 * inch, 1.2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b2b4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ]))
        story.append(table)

        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Total: {len(produits)} produits",
                               ParagraphStyle('Total', parent=styles['Normal'], fontSize=10,
                                              fontName='Helvetica-Bold')))

        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph("MDL Business - Tous droits réservés",
                               ParagraphStyle('Footer', parent=styles['Normal'],
                                              fontSize=7, textColor=colors.HexColor('#6c757d'), alignment=TA_CENTER)))

        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    @staticmethod
    def generer_liste_commandes(commandes, statut_filtre=""):
        """Génère un PDF avec la liste des commandes"""
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=60, leftMargin=60,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()
        story = []

        # ============================================
        # LOGO ET TITRE
        # ============================================
        titre = "Liste des commandes"
        sous_titre = f"Filtre: {statut_filtre.replace('_', ' ').title()}" if statut_filtre else "Toutes les commandes"
        PDFService._ajouter_logo_et_titre(story, titre, sous_titre)

        # Tableau
        data = [['#', 'Référence', 'Client', 'Total', 'Statut', 'Date']]

        for i, c in enumerate(commandes, 1):
            data.append([
                str(i),
                c.reference,
                f"{c.prenom} {c.nom}",
                f"{c.total:.2f} $",
                c.statut.replace('_', ' ').title(),
                c.date_creation.strftime('%d/%m/%Y %H:%M')
            ])

        table = Table(data, colWidths=[0.5 * inch, 1.8 * inch, 2 * inch, 1 * inch, 1.2 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b2b4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ]))
        story.append(table)

        story.append(Spacer(1, 15))
        story.append(Paragraph(f"Total: {len(commandes)} commande(s)",
                               ParagraphStyle('Total', parent=styles['Normal'],
                                              fontSize=10, fontName='Helvetica-Bold')))

        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph("MDL Business - Tous droits réservés",
                               ParagraphStyle('Footer', parent=styles['Normal'],
                                              fontSize=7, textColor=colors.HexColor('#6c757d'), alignment=TA_CENTER)))

        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    @staticmethod
    def generer_liste_utilisateurs(utilisateurs, role_filtre=""):
        """Génère un PDF avec la liste des utilisateurs"""
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=60, leftMargin=60,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()
        story = []

        # ============================================
        # LOGO ET TITRE
        # ============================================
        titre = "Liste des utilisateurs"
        sous_titre = f"Filtre: {role_filtre.title()}" if role_filtre else "Tous les utilisateurs"
        PDFService._ajouter_logo_et_titre(story, titre, sous_titre)

        # Tableau
        data = [['#', 'Email', 'Nom', 'Rôle', 'Inscription', 'Statut']]

        for i, u in enumerate(utilisateurs, 1):
            data.append([
                str(i),
                u.email,
                f"{u.prenom or ''} {u.nom or ''}".strip() or '-',
                u.role.title() if u.role else 'Client',
                u.date_inscription.strftime('%d/%m/%Y') if u.date_inscription else '-',
                'Actif' if u.est_actif else 'Inactif'
            ])

        table = Table(data, colWidths=[0.5 * inch, 2 * inch, 1.8 * inch, 1.2 * inch, 1.2 * inch, 1 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b2b4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ]))
        story.append(table)

        story.append(Spacer(1, 15))
        story.append(Paragraph(f"Total: {len(utilisateurs)} utilisateur(s)",
                               ParagraphStyle('Total', parent=styles['Normal'],
                                              fontSize=10, fontName='Helvetica-Bold')))

        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph("MDL Business - Tous droits réservés",
                               ParagraphStyle('Footer', parent=styles['Normal'],
                                              fontSize=7, textColor=colors.HexColor('#6c757d'), alignment=TA_CENTER)))

        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    @staticmethod
    def generer_liste_categories(categories):
        """Génère un PDF avec la liste des catégories"""
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=60, leftMargin=60,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()
        story = []

        # ============================================
        # LOGO ET TITRE
        # ============================================
        PDFService._ajouter_logo_et_titre(story, "Liste des catégories")

        # Tableau
        data = [['#', 'Nom', 'Slug', 'Produits', 'Statut']]

        for i, cat in enumerate(categories, 1):
            data.append([
                str(i),
                cat.nom,
                cat.slug,
                str(len(cat.produits)),
                'Actif' if cat.est_active else 'Inactif'
            ])

        table = Table(data, colWidths=[0.5 * inch, 2 * inch, 1.5 * inch, 1 * inch, 1.2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b2b4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ]))
        story.append(table)

        story.append(Spacer(1, 15))
        story.append(Paragraph(f"Total: {len(categories)} catégorie(s)",
                               ParagraphStyle('Total', parent=styles['Normal'],
                                              fontSize=10, fontName='Helvetica-Bold')))

        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph("MDL Business - Tous droits réservés",
                               ParagraphStyle('Footer', parent=styles['Normal'],
                                              fontSize=7, textColor=colors.HexColor('#6c757d'), alignment=TA_CENTER)))

        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        return pdf