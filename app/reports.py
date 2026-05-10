"""
Hilltop Tea — Reports Blueprint.

PDF export functionality using reportlab.
"""
from io import BytesIO

from flask import Blueprint, make_response, request
from flask_login import current_user, login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app import db
from app.models import Employee, Payment, ProductionRecord
from app.utils import month_range

reports_bp = Blueprint('reports', __name__)


def _get_payroll_data(month_str: str, group_filter: str = None):
    """
    Get payroll data for PDF generation.

    Args:
        month_str: Month in 'YYYY-MM' format.
        group_filter: Optional filter by employee group.

    Returns:
        Tuple of (data list, grand totals dict).
    """
    first_day, last_day = month_range(month_str)

    from sqlalchemy import func

    query = db.session.query(
        Employee.id,
        Employee.name,
        Employee.worker_group,
        func.coalesce(func.sum(ProductionRecord.cartons), 0).label('carton_total'),
        func.coalesce(func.sum(ProductionRecord.daily_wage), 0).label('wage_total'),
        func.coalesce(func.sum(Payment.amount), 0).label('paid_total'),
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
        query = query.filter(Employee.worker_group == group_filter)

    results = query.all()

    data = []
    grand_wage = 0
    grand_paid = 0
    grand_cartons = 0

    for emp_id, emp_name, emp_group, carton_total, wage_total, paid_total in results:
        balance = wage_total - paid_total
        data.append({
            'name': emp_name,
            'group': emp_group.value if emp_group else 'unknown',
            'cartons': int(carton_total),
            'wage': float(wage_total),
            'paid': float(paid_total),
            'balance': balance,
        })
        grand_wage += wage_total
        grand_paid += paid_total
        grand_cartons += carton_total

    grand_balance = grand_wage - grand_paid

    return data, {
        'cartons': grand_cartons,
        'wage': grand_wage,
        'paid': grand_paid,
        'balance': grand_balance,
    }


@reports_bp.route('/wage-sheet.pdf')
@login_required
def wage_sheet_pdf():
    """
    Generate and stream a PDF wage sheet for the selected month.

    GET: Generate PDF and send as attachment.
    """
    month_str = request.args.get('month')
    group_filter = request.args.get('group')

    if not month_str:
        from flask import flash, redirect, url_for
        flash_error('Month parameter is required.')
        return redirect(url_for('payroll.index'))

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

    from datetime import datetime

    # Get payroll data
    data, grand_totals = _get_payroll_data(month_str, group_filter)

    # Create buffer
    buffer = BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    # Get styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=colors.HexColor('#1e3932'),
        alignment=1,  # Center
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#c9a96e'),
        alignment=1,
        spaceAfter=12,
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        spaceAfter=6,
    )

    right_style = ParagraphStyle(
        'Right',
        parent=normal_style,
        alignment=2,  # Right
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.grey,
        alignment=1,
    )

    # Build story
    story = []

    # Title
    story.append(Paragraph('HILLTOP TEA', title_style))
    story.append(Paragraph('MONTHLY WAGE SHEET', subtitle_style))

    # Month and metadata
    month_label = f'Month: {month_str}'
    generated_date = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    prepared_by = f'Prepared by: {current_user.username}'

    story.append(Paragraph(month_label, right_style))
    story.append(Paragraph(generated_date, right_style))
    story.append(Paragraph(prepared_by, right_style))
    story.append(Spacer(1, 6*mm))

    # Horizontal rule
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#1e3932')))
    story.append(Spacer(1, 6*mm))

    # Build table data
    table_data = [['S/N', 'Name', 'Group', 'Cartons', 'Wage (₦)', 'Paid (₦)', 'Balance (₦)']]

    for idx, row in enumerate(data, 1):
        balance_color = colors.red if row['balance'] > 0 else colors.green
        table_data.append([
            str(idx),
            row['name'],
            row['group'].title(),
            str(row['cartons']),
            f'₦{row["wage"]:,.2f}',
            f'₦{row["paid"]:,.2f}',
            f'₦{row["balance"]:,.2f}',
        ])

    # Grand totals row
    table_data.append([
        '',
        'GRAND TOTALS',
        '',
        str(grand_totals['cartons']),
        f'₦{grand_totals["wage"]:,.2f}',
        f'₦{grand_totals["paid"]:,.2f}',
        f'₦{grand_totals["balance"]:,.2f}',
    ])

    # Create table
    table = Table(table_data, colWidths=[20*mm, 40*mm, 20*mm, 15*mm, 25*mm, 25*mm, 25*mm])

    # Table style
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3932')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

        # Data rows - alternating colors
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f2eb')]),

        # Grand totals row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c9a96e')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        # Alignment
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # S/N
        ('ALIGN', (1, 1), (2, -1), 'LEFT'),   # Name, Group
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Cartons
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),  # Currency columns

        # Borders
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#1e3932')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#c9a96e')),
    ])

    table.setStyle(table_style)
    story.append(table)

    # Signature block
    story.append(Spacer(1, 40*mm))

    sig_data = [
        ['Prepared by: _______________', 'Date: _______________'],
        ['Authorised by: _______________', 'Date: _______________'],
    ]

    sig_table = Table(sig_data, colWidths=[80*mm, 40*mm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(sig_table)

    # Footer
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph('CONFIDENTIAL — HILLTOP TEA INTERNAL DOCUMENT', footer_style))

    # Build PDF
    doc.build(story)

    # Seek to beginning
    buffer.seek(0)

    # Create response
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=hilltop_wage_{month_str}.pdf'

    return response
