"""
Hilltop Tea — Reports and PDF Export Blueprint.

Handles PDF wage sheet generation using reportlab.
"""
from datetime import datetime
from io import BytesIO

from flask import Blueprint, make_response, render_template, request
from flask_login import login_required
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable, PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle
)
from reportlab.platypus.paragraph import Paragraph

from app import db
from app.models import Employee, Payment, ProductionRecord
from app.utils import month_range

reports_bp = Blueprint('reports', __name__)


def get_payroll_data(first_day, last_day, group_filter=None):
    """
    Get payroll data for PDF generation.

    Args:
        first_day: First day of month (datetime).
        last_day: Last day of month (datetime).
        group_filter: Optional filter by employee group.

    Returns:
        List of payroll row dictionaries.
    """
    query = db.session.query(
        Employee.id,
        Employee.name,
        Employee.group,
        db.func.coalesce(db.func.sum(ProductionRecord.cartons), 0).label('carton_total'),
        db.func.coalesce(db.func.sum(ProductionRecord.daily_wage), 0).label('wage_total'),
        db.func.coalesce(db.func.sum(Payment.amount), 0).label('paid_total')
    ).outerjoin(
        ProductionRecord,
        (ProductionRecord.employee_id == Employee.id) &
        (ProductionRecord.date >= first_day) &
        (ProductionRecord.date <= last_day)
    ).outerjoin(
        Payment,
        (Payment.employee_id == Employee.id) &
        (Payment.payment_date >= first_day) &
        (Payment.payment_date <= last_day)
    ).group_by(Employee.id).order_by(Employee.name)

    if group_filter and group_filter in ('production', 'wrapping'):
        query = query.filter(Employee.group == group_filter)

    results = query.all()

    payroll_data = []
    for row in results:
        wage_total = float(row.wage_total)
        paid_total = float(row.paid_total)
        balance = wage_total - paid_total

        payroll_data.append({
            'name': row.name,
            'group': row.group,
            'cartons': int(row.carton_total),
            'wage': wage_total,
            'paid': paid_total,
            'balance': balance
        })

    return payroll_data


@reports_bp.route('/wage-sheet')
@login_required
def wage_sheet_pdf():
    """
    Generate and stream a PDF wage sheet for the selected month.

    Query parameters:
        month: YYYY-MM string (required)
        group: Optional filter by employee group
    """
    month_str = request.args.get('month')
    if not month_str:
        return "Month parameter is required", 400

    try:
        first_day, last_day = month_range(month_str)
    except ValueError:
        return f"Invalid month format: {month_str}", 400

    group_filter = request.args.get('group')

    # ═══════════════════════════════════════════════════════════════
    # PPP: generate_wage_sheet_pdf(month_str, group_filter, user)
    # ═══════════════════════════════════════════════════════════════
    # PRE-CONDITIONS:
    #   - month_str: 'YYYY-MM' string, validated before calling this function
    #   - user: current_user (for "Prepared by" line)
    #
    # ALGORITHM:
    #   1. Reuse payroll aggregation helper function (DRY — same logic as payroll_view)
    #   2. Create BytesIO buffer
    #   3. Instantiate reportlab SimpleDocTemplate (A4, 20mm margins, buffer)
    #   4. Build story list (platypus elements):
    #      a. Spacer + "HILLTOP TEA" in HexColor(#1e3932), Cormorant-equivalent font,
    #         28pt, centred
    #      b. "MONTHLY WAGE SHEET" subtitle, 14pt, gold HexColor(#c9a96e)
    #      c. Month label, generated date, prepared-by line — right-aligned
    #      d. Horizontal rule (HRFlowable, green)
    #      e. Table with 7 columns:
    #            S/N | Name | Group | Cartons | Wage (₦) | Paid (₦) | Balance (₦)
    #         Header row: bg=#1e3932, white text, bold
    #         Data rows: alternating #f5f2eb / white
    #         Balance column: red text if positive, green if negative
    #         All currency cells: right-aligned, Courier font for alignment
    #      f. Grand totals row: bold, bg=#c9a96e
    #      g. Spacer(40)
    #      h. Two-column signature block:
    #            "Prepared by: _______________"  |  "Date: _______________"
    #            "Authorised by: _______________"  |  "Date: _______________"
    #      i. Footer paragraph: "CONFIDENTIAL — HILLTOP TEA INTERNAL DOCUMENT"
    #   5. Call doc.build(story)
    #   6. Seek buffer to 0
    #   7. Return Flask Response(buffer.getvalue(),
    #         mimetype='application/pdf',
    #         headers={'Content-Disposition':
    #           f'attachment; filename=hilltop_wage_{month_str}.pdf'})
    #
    # POST-CONDITIONS:
    #   - Valid PDF streamed to client
    #   - No temp files written to disk (Vercel has no writable FS)
    # ═══════════════════════════════════════════════════════════════

    # Get payroll data
    payroll_data = get_payroll_data(first_day, last_day, group_filter)

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=colors.HexColor('#1e3932'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica',
        fontSize=14,
        textColor=colors.HexColor('#c9a96e'),
        alignment=TA_CENTER,
        spaceAfter=24
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        spaceAfter=6
    )
    right_style = ParagraphStyle(
        'CustomRight',
        parent=normal_style,
        alignment=TA_RIGHT
    )
    footer_style = ParagraphStyle(
        'CustomFooter',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )

    # Build story
    story = []

    # Title
    story.append(Paragraph("HILLTOP TEA", title_style))
    story.append(Paragraph("MONTHLY WAGE SHEET", subtitle_style))

    # Month and metadata
    month_name = first_day.strftime('%B %Y')
    generated_date = datetime.now().strftime('%d %B %Y')
    prepared_by = current_user.username if current_user.is_authenticated else 'System'

    meta_text = f"""
    <b>Month:</b> {month_name}<br/>
    <b>Generated:</b> {generated_date}<br/>
    <b>Prepared by:</b> {prepared_by}
    """
    story.append(Paragraph(meta_text, right_style))
    story.append(Spacer(1, 12))

    # Horizontal rule
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#1e3932')))
    story.append(Spacer(1, 12))

    # Build table data
    table_data = [
        ['S/N', 'Name', 'Group', 'Cartons', 'Wage (₦)', 'Paid (₦)', 'Balance (₦)']
    ]

    grand_totals = {'cartons': 0, 'wage': 0, 'paid': 0, 'balance': 0}

    for idx, row in enumerate(payroll_data, 1):
        grand_totals['cartons'] += row['cartons']
        grand_totals['wage'] += row['wage']
        grand_totals['paid'] += row['paid']
        grand_totals['balance'] += row['balance']

        balance_color = colors.red if row['balance'] > 0 else colors.green

        table_data.append([
            str(idx),
            row['name'],
            row['group'].title(),
            str(row['cartons']),
            f"₦{row['wage']:,.2f}",
            f"₦{row['paid']:,.2f}",
            f'<font color="{balance_color.hexval}">₦{row["balance"]:,.2f}</font>'
        ])

    # Grand totals row
    table_data.append([
        '',
        '<b>GRAND TOTALS</b>',
        '',
        f'<b>{grand_totals["cartons"]}</b>',
        f'<b>₦{grand_totals["wage"]:,.2f}</b>',
        f'<b>₦{grand_totals["paid"]:,.2f}</b>',
        f'<b>₦{grand_totals["balance"]:,.2f}</b>'
    ])

    # Create table
    table = Table(table_data, colWidths=[1*cm, 4*cm, 2*cm, 1.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])

    # Table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3932')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f2eb')]),
        ('FONTNAME', (4, 1), (6, -2), 'Courier'),
        ('ALIGN', (4, 1), (6, -2), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c9a96e')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ])
    table.setStyle(table_style)

    story.append(table)
    story.append(Spacer(1, 40))

    # Signature block
    signature_data = [
        ['', ''],
        ['Prepared by:', 'Date:'],
        ['___________________', '___________________'],
        ['', ''],
        ['Authorised by:', 'Date:'],
        ['___________________', '___________________'],
    ]
    signature_table = Table(signature_data, colWidths=[6*cm, 6*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(signature_table)

    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph("CONFIDENTIAL — HILLTOP TEA INTERNAL DOCUMENT", footer_style))

    # Build PDF
    doc.build(story)

    # Prepare response
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=hilltop_wage_{month_str}.pdf'

    return response
