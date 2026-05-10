#!/usr/bin/env python3
"""
Hilltop Tea — Documentation PDF Generator.

Converts all .md files in the docs/ directory to branded PDFs
using python-markdown and reportlab. No WeasyPrint required.

Usage:
    cd hilltop_tea/docs/
    python generate_pdfs.py

Output:
    docs/pdf/<filename>.pdf  (one per .md file, excluding this script)
"""
import os
import sys
from pathlib import Path
from io import BytesIO

from bs4 import BeautifulSoup
from markdown import markdown
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
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.rl_config import defaultPageSize


# Brand colors
TEA_GREEN = colors.HexColor('#1e3932')
TEA_GOLD = colors.HexColor('#c9a96e')
TEA_CREAM = colors.HexColor('#f5f2eb')


class BrandedDocTemplate(BaseDocTemplate):
    """Custom document template with branded header and footer."""

    def __init__(self, filename, **kw):
        self.title = kw.pop('title', 'Hilltop Tea Documentation')
        super().__init__(filename, **kw)

    def afterFlowable(self, flowable):
        """Called after each flowable is added."""
        pass

    def beforePage(self):
        """Called before each page is rendered."""
        canvas = self.canv
        canvas.saveState()

        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(TEA_GREEN)
        canvas.drawString(20*mm, 280*mm, self.title)

        # Page number
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(190*mm, 280*mm, f'Page {self.page}')

        # Decorative line
        canvas.setStrokeColor(TEA_GOLD)
        canvas.setLineWidth(1)
        canvas.line(20*mm, 278*mm, 190*mm, 278*mm)

        canvas.restoreState()


def parse_markdown_to_elements(md_content, title):
    """Parse markdown content into reportlab flowables."""
    elements = []

    # Convert markdown to HTML
    html = markdown(md_content, extensions=['tables', 'fenced_code'])

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Get styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=TEA_GREEN,
        spaceAfter=12,
    )

    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=TEA_GREEN,
        spaceAfter=12,
        spaceBefore=12,
    )

    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=TEA_GOLD,
        spaceAfter=8,
        spaceBefore=8,
    )

    heading3_style = ParagraphStyle(
        'Heading3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=TEA_GREEN,
        spaceAfter=6,
        spaceBefore=6,
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        spaceAfter=6,
        leading=14,
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        backColor=colors.HexColor('#f5f5f5'),
        leftIndent=10,
        rightIndent=10,
        spaceAfter=6,
    )

    # Process elements
    for element in soup.find_all(True):
        tag = element.name

        if tag == 'h1':
            text = element.get_text().strip()
            elements.append(Paragraph(text, heading1_style))

        elif tag == 'h2':
            text = element.get_text().strip()
            elements.append(Paragraph(text, heading2_style))

        elif tag == 'h3':
            text = element.get_text().strip()
            elements.append(Paragraph(text, heading3_style))

        elif tag == 'p':
            text = element.get_text().strip()
            if text:
                elements.append(Paragraph(text, normal_style))

        elif tag == 'ul':
            for li in element.find_all('li', recursive=False):
                text = li.get_text().strip()
                if text:
                    elements.append(Paragraph(f'• {text}', normal_style))

        elif tag == 'ol':
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                text = li.get_text().strip()
                if text:
                    elements.append(Paragraph(f'{i}. {text}', normal_style))

        elif tag == 'pre':
            code = element.get_text().strip()
            if code:
                elements.append(Paragraph(code, code_style))

        elif tag == 'code':
            # Inline code
            code = element.get_text().strip()
            if code:
                elements.append(Paragraph(f'<code>{code}</code>', normal_style))

        elif tag == 'blockquote':
            text = element.get_text().strip()
            if text:
                elements.append(Paragraph(text, ParagraphStyle(
                    'Blockquote',
                    parent=normal_style,
                    leftIndent=20,
                    textColor=colors.grey,
                )))

        elif tag == 'hr':
            elements.append(HRFlowable(width='100%', thickness=1, color=TEA_GOLD))

        elif tag == 'table':
            # Process table
            rows = []
            for tr in element.find_all('tr'):
                row = []
                for cell in tr.find_all(['td', 'th']):
                    text = cell.get_text().strip()
                    row.append(text)
                if row:
                    rows.append(row)

            if rows:
                table = Table(rows)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), TEA_GREEN),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 6*mm))

    return elements


def generate_pdf(md_file, output_dir):
    """Generate PDF from a markdown file."""
    try:
        # Read markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Get title from first heading or filename
        title = md_file.stem.replace('_', ' ').title()

        # Parse markdown
        elements = parse_markdown_to_elements(md_content, title)

        # Create output buffer
        buffer = BytesIO()

        # Create document
        doc = BrandedDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=30*mm,
            bottomMargin=20*mm,
            title=title,
        )

        # Build PDF
        doc.build(elements)

        # Write to file
        output_path = output_dir / f'{md_file.stem}.pdf'
        with open(output_path, 'wb') as f:
            f.write(buffer.getvalue())

        print(f'Generated: {output_path}')
        return True

    except Exception as e:
        print(f'Error processing {md_file}: {e}', file=sys.stderr)
        return False


def main():
    """Main function to generate all PDFs."""
    # Get script directory
    script_dir = Path(__file__).parent

    # Create output directory
    output_dir = script_dir / 'pdf'
    output_dir.mkdir(exist_ok=True)

    # Find all markdown files
    md_files = sorted(script_dir.glob('*.md'))

    # Skip this script if it's in the list
    md_files = [f for f in md_files if f.name != 'generate_pdfs.py']

    if not md_files:
        print('No markdown files found in docs/ directory')
        return

    print(f'Found {len(md_files)} markdown files')
    print('Generating PDFs...')

    success_count = 0
    for md_file in md_files:
        if generate_pdf(md_file, output_dir):
            success_count += 1

    print(f'\nCompleted: {success_count}/{len(md_files)} PDFs generated')
    print(f'Output directory: {output_dir}')


if __name__ == '__main__':
    main()
