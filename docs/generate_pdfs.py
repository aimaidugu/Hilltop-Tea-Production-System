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

from markdown import markdown
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable, PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle
)
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tableofcontents import TableOfContents


def parse_markdown_to_elements(md_content, styles):
    """
    Parse Markdown content and convert to reportlab flowables.

    Args:
        md_content: Markdown string content.
        styles: ReportLab styles object.

    Returns:
        List of reportlab flowables.
    """
    html_content = markdown(md_content, extensions=['tables', 'fenced_code'])
    soup = BeautifulSoup(html_content, 'html.parser')

    elements = []

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'table', 'pre', 'blockquote']):
        tag = element.name

        if tag == 'h1':
            text = element.get_text()
            elements.append(Paragraph(text, styles['Heading1']))
            elements.append(Spacer(1, 12))

        elif tag == 'h2':
            text = element.get_text()
            elements.append(Paragraph(text, styles['Heading2']))
            elements.append(Spacer(1, 8))

        elif tag == 'h3':
            text = element.get_text()
            elements.append(Paragraph(text, styles['Heading3']))
            elements.append(Spacer(1, 6))

        elif tag == 'h4':
            text = element.get_text()
            elements.append(Paragraph(text, styles['Heading4']))
            elements.append(Spacer(1, 4))

        elif tag == 'p':
            text = element.get_text()
            if text.strip():
                elements.append(Paragraph(text, styles['BodyText']))
                elements.append(Spacer(1, 6))

        elif tag in ['ul', 'ol']:
            list_items = element.find_all('li', recursive=False)
            for li in list_items:
                text = li.get_text()
                bullet = '•' if tag == 'ul' else '1.'
                elements.append(Paragraph(f'{bullet} {text}', styles['BodyText']))
                elements.append(Spacer(1, 4))
            elements.append(Spacer(1, 6))

        elif tag == 'table':
            table_data = []
            rows = element.find_all('tr')
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text() for cell in cells]
                table_data.append(row_data)

            if table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3932')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))

        elif tag == 'pre':
            code_text = element.get_text()
            elements.append(Paragraph('<font face="Courier" size="8">' + code_text + '</font>', styles['Code']))
            elements.append(Spacer(1, 6))

        elif tag == 'blockquote':
            text = element.get_text()
            elements.append(Paragraph(f'<i>{text}</i>', styles['BodyText']))
            elements.append(Spacer(1, 6))

    return elements


def create_pdf(md_file_path, output_dir):
    """
    Create a PDF from a Markdown file.

    Args:
        md_file_path: Path to the Markdown file.
        output_dir: Directory to save the PDF.

    Returns:
        Path to the generated PDF or None if failed.
    """
    try:
        # Read Markdown content
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Create output path
        md_filename = Path(md_file_path).stem
        output_path = os.path.join(output_dir, f'{md_filename}.pdf')

        # Create buffer
        buffer = BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=20*mm
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#1e3932'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))

        styles.add(ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontName='Helvetica',
            fontSize=14,
            textColor=colors.HexColor('#c9a96e'),
            alignment=TA_CENTER,
            spaceAfter=24
        ))

        styles.add(ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            spaceAfter=6
        ))

        styles.add(ParagraphStyle(
            'Code',
            parent=styles['Code'],
            fontName='Courier',
            fontSize=8,
            leading=10,
            leftIndent=20,
            spaceAfter=6
        ))

        # Parse Markdown to elements
        elements = parse_markdown_to_elements(md_content, styles)

        # Add title page
        title = Path(md_file_path).stem.replace('_', ' ').title()
        elements.insert(0, Paragraph('HILLTOP TEA', styles['CustomTitle']))
        elements.insert(1, Paragraph(title, styles['CustomSubtitle']))
        elements.insert(2, Spacer(1, 48))

        # Build PDF
        doc.build(elements)

        # Write to file
        with open(output_path, 'wb') as f:
            f.write(buffer.getvalue())

        return output_path

    except Exception as e:
        print(f'Error processing {md_file_path}: {e}')
        return None


def main():
    """Main function to generate PDFs from all Markdown files."""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create output directory
    output_dir = os.path.join(script_dir, 'pdf')
    os.makedirs(output_dir, exist_ok=True)

    # Find all Markdown files
    md_files = []
    for file in os.listdir(script_dir):
        if file.endswith('.md') and file != 'generate_pdfs.py':
            md_files.append(os.path.join(script_dir, file))

    if not md_files:
        print('No Markdown files found in the current directory.')
        return

    print(f'Found {len(md_files)} Markdown files to convert.')

    # Generate PDFs
    success_count = 0
    for md_file in md_files:
        output_path = create_pdf(md_file, output_dir)
        if output_path:
            print(f'Generated: {output_path}')
            success_count += 1

    print(f'\nCompleted: {success_count}/{len(md_files)} PDFs generated.')
    print(f'Output directory: {output_dir}')


if __name__ == '__main__':
    main()
