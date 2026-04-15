from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

def export_to_pdf(filename, tournament_name, date_str, entries, target_teiler, info_text=None, mode="teiler"):
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
    if mode == "teiler":
        elements.append(Paragraph(f"Zielteiler: {target_teiler:.1f}".replace('.', ','), normal_style))
    elements.append(Spacer(1, 1*cm))

    # Process classes if any
    has_classes = any(e.get('klasse') for e in entries)

    if has_classes:
        current_class = object() # Dummy object

        for entry in entries:
            cls = entry.get('klasse')
            if cls != current_class:
                current_class = cls
                header_name = cls if cls else "Nicht zugeordnet"

                # Add class header
                elements.append(Spacer(1, 0.5*cm))
                class_style = ParagraphStyle('ClassHeader', parent=styles['Heading2'], textColor=colors.darkorange)
                elements.append(Paragraph(header_name, class_style))
                elements.append(Spacer(1, 0.2*cm))

                # Add table headers for this class
                headers = ["Nr.", "Name", "Teiler", "Abweichung"] if mode == "teiler" else ["Nr.", "Name", "Ringzahl"]
                col_widths = [2*cm, 9*cm, 3*cm, 3*cm] if mode == "teiler" else [2*cm, 10*cm, 5*cm]
                data = [headers]
                table_entries = [e for e in entries if e.get('klasse') == cls]

                for r_entry in table_entries:
                    if mode == "teiler":
                        diff = abs(r_entry['teiler'] - target_teiler)
                        row = [
                            str(r_entry['number']) if r_entry['number'] is not None else "",
                            r_entry['name'],
                            f"{r_entry['teiler']:.1f}".replace('.', ','),
                            f"{diff:.1f}".replace('.', ',')
                        ]
                    else:
                        row = [
                            str(r_entry['number']) if r_entry['number'] is not None else "",
                            r_entry['name'],
                            f"{r_entry.get('ringzahl', 0.0):.1f}".replace('.', ',')
                        ]
                    data.append(row)

                table = Table(data, colWidths=col_widths)
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
    else:
        # Table Data
        headers = ["Nr.", "Name", "Teiler", "Abweichung"] if mode == "teiler" else ["Nr.", "Name", "Ringzahl"]
        data = [headers]

        for entry in entries:
            if mode == "teiler":
                diff = abs(entry['teiler'] - target_teiler)
                row = [
                    str(entry['number']) if entry['number'] is not None else "",
                    entry['name'],
                    f"{entry['teiler']:.1f}".replace('.', ','),
                    f"{diff:.1f}".replace('.', ',')
                ]
            else:
                row = [
                    str(entry['number']) if entry['number'] is not None else "",
                    entry['name'],
                    f"{entry.get('ringzahl', 0.0):.1f}".replace('.', ',')
                ]
            data.append(row)

        # Table Style
        col_widths = [2*cm, 9*cm, 3*cm, 3*cm] if mode == "teiler" else [2*cm, 10*cm, 5*cm]
        table = Table(data, colWidths=col_widths)
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
