from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

def export_to_pdf(filename, tournament_name, date_str, entries, target_teiler, info_text=None):
    """
    Exports the given entries to a PDF file.
    entries: List of dicts, expected to be already sorted.
    info_text: Optional string to display below title (e.g. sorting/filter info).
    """
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = styles['Title']
    elements.append(Paragraph(tournament_name, title_style))
    elements.append(Spacer(1, 0.5*cm))

    # Info Text (Sorting/Filter)
    normal_style = styles['Normal']
    if info_text:
        elements.append(Paragraph(info_text, normal_style))
        elements.append(Spacer(1, 0.2*cm))

    # Date & Info
    elements.append(Paragraph(f"Datum: {date_str}", normal_style))
    elements.append(Paragraph(f"Zielteiler: {target_teiler:.1f}".replace('.', ','), normal_style))
    elements.append(Spacer(1, 1*cm))

    # Table Data
    data = [["Nr.", "Name", "Teiler", "Abweichung"]]

    for rank, entry in enumerate(entries, 1):
        diff = abs(entry['teiler'] - target_teiler)
        row = [
            str(entry['number']),
            entry['name'],
            f"{entry['teiler']:.1f}".replace('.', ','),
            f"{diff:.1f}".replace('.', ',')
        ]
        data.append(row)

    # Table Style
    table = Table(data, colWidths=[2*cm, 9*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Left align names
    ]))

    elements.append(table)

    # Build
    try:
        doc.build(elements)
        return True
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return False
