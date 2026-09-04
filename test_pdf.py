import os
from datetime import datetime
from flask import url_for, current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas


class PDFService:
    """Service de génération de PDF pour les commandes avec ReportLab"""

    @staticmethod
    def generer_facture(commande):
        """
        Génère une facture PDF pour une commande avec logo
        """
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)

        styles = getSampleStyleSheet()

        # ============================================
        # RECHERCHER LE LOGO
        # ============================================
        logo_path = None
        possible_paths = [
            os.path.join('app', 'views', 'static', 'images', 'logos', 'logo.png'),
            os.path.join('app', 'views', 'static', 'images', 'logos', 'logo.jpg'),
            os.path.join('app', 'views', 'static', 'images', 'logo.png'),
            os.path.join('app', 'views', 'static', 'logo.png'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logo_path = path
                break

        # ============================================
        # STYLES PERSONNALISÉS
        # ============================================
        style_title = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontSize=20,
            textColor=colors.HexColor('#0b2b4a'),
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )

        style_subtitle = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER,
            spaceAfter=20
        )

        style_heading = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#0b2b4a'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )

        style_total = ParagraphStyle(
            'TotalStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0b2b4a'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        )

        style_footer = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER
        )

        # ============================================
        # ÉLÉMENTS DU PDF
        # ============================================
        story = []

        # ============================================
        # LOGO + EN-TÊTE
        # ============================================
        # Créer un tableau pour le logo et le titre
        if logo_path:
            try:
                logo = Image(logo_path, width=1.5 * inch, height=0.75 * inch)
                logo.hAlign = 'CENTER'

                # Tableau avec 2 colonnes: logo + texte
                header_data = [
                    [logo,
                     Paragraph("<b>MDL BUSINESS</b><br/><font size='10' color='#6c757d'>Facture de commande</font>",
                               ParagraphStyle('HeaderText', parent=styles['Normal'],
                                              alignment=TA_CENTER, fontSize=14, textColor=colors.HexColor('#0b2b4a')))]
                ]
                header_table = Table(header_data, colWidths=[1.8 * inch, 3.5 * inch])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (0, 0), 0),
                    ('RIGHTPADDING', (1, 0), (1, 0), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(header_table)
            except Exception as e:
                print(f"⚠️ Erreur chargement logo: {e}")
                # Fallback: titre sans logo
                story.append(Paragraph("MDL BUSINESS", style_title))
                story.append(Paragraph("Facture de commande", style_subtitle))
        else:
            # Pas de logo trouvé
            story.append(Paragraph("MDL BUSINESS", style_title))
            story.append(Paragraph("Facture de commande", style_subtitle))
            story.append(Paragraph("Logo non trouvé - Veuillez ajouter votre logo",
                                   ParagraphStyle('NoLogo', parent=styles['Normal'],
                                                  alignment=TA_CENTER, fontSize=8, textColor=colors.red)))

        story.append(Spacer(1, 10))

        # Référence et date
        story.append(Paragraph(f"Commande <b>#{commande.reference}</b>", style_heading))
        story.append(Paragraph(f"Date: {commande.date_creation.strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
        story.append(Paragraph(f"Statut: {commande.statut.replace('_', ' ').title()}", styles['Normal']))
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0b2b4a')))
        story.append(Spacer(1, 15))

        # ============================================
        # INFOS CLIENT ET LIVRAISON
        # ============================================
        # Créer un tableau 2 colonnes pour client et livraison
        info_data = [
            [
                Paragraph("<b>👤 Client</b>", style_heading),
                Paragraph("<b>📍 Livraison</b>", style_heading)
            ],
            [
                Paragraph(
                    f"{commande.prenom} {commande.nom}<br/>{commande.email}<br/>{'Tél: ' + commande.telephone if commande.telephone else ''}",
                    styles['Normal']),
                Paragraph(
                    f"{commande.adresse_livraison.replace(chr(10), '<br/>')}<br/>{commande.code_postal} {commande.ville}<br/>{commande.pays}",
                    styles['Normal'])
            ]
        ]

        info_table = Table(info_data, colWidths=[3.2 * inch, 3.2 * inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Spacer(1, 15))

        # ============================================
        # TABLEAU DES ARTICLES
        # ============================================
        story.append(Paragraph("<b>📦 Articles commandés</b>", style_heading))
        story.append(Spacer(1, 10))

        # Données du tableau
        data = [
            ['Produit', 'Qté', 'Prix unit.', 'Total']
        ]

        for ligne in commande.lignes:
            data.append([
                ligne.nom_produit,
                str(ligne.quantite),
                f"{ligne.prix_unitaire:.2f} $",
                f"{ligne.prix_unitaire * ligne.quantite:.2f} $"
            ])

        # Ligne total
        data.append(['', '', 'TOTAL', f"{commande.total:.2f} $"])

        # Créer le tableau
        table = Table(data, colWidths=[3 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b2b4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#0b2b4a')),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#0b2b4a')),
        ]))

        story.append(table)
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Spacer(1, 15))

        # ============================================
        # PIED DE PAGE
        # ============================================
        story.append(Paragraph("Merci pour votre confiance !",
                               ParagraphStyle('Thanks', parent=styles['Normal'],
                                              alignment=TA_CENTER, fontSize=12, textColor=colors.HexColor('#0b2b4a'))))
        story.append(Spacer(1, 5))

        # Mode de paiement
        paiement_info = f"Mode de paiement: {commande.mode_paiement or 'Non spécifié'}"
        if commande.transaction_id:
            paiement_info += f"  |  Transaction: {commande.transaction_id}"
        story.append(Paragraph(paiement_info, styles['Normal']))

        story.append(Spacer(1, 20))

        # Footer
        story.append(Paragraph("MDL Business - Tous droits réservés", style_footer))
        story.append(Paragraph(f"Facture générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", style_footer))

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