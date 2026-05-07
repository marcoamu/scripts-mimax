#!/usr/bin/env python3
"""
MD to Word Converter with Better Formatting
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import io
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.section import WD_ORIENT

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileData(BaseModel):
    name: str
    content: str

class MDToWordRequest(BaseModel):
    title: str = "Documentación"
    files: list[FileData]

def add_code_block(doc, code, language=""):
    """Add a nicely formatted code block with border and background"""
    # Create paragraph with left border effect using shading
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.2

    # Add code text
    if language:
        run = p.add_run(f"// {language}\n")
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(100, 100, 100)
        run.font.italic = True

    run = p.add_run(code)
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(40, 40, 40)

    # Add shading to entire paragraph (light gray background)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), 'E8E8E8')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:val'), 'clear')
    pPr.append(shd)

    # Add border
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '12')
    left.set(qn('w:space'), '4')
    left.set(qn('w:color'), 'CCCCCC')
    pBdr.append(left)
    pPr.append(pBdr)

def add_styled_heading(doc, text, level):
    """Add a heading with custom styling"""
    p = doc.add_heading(level=level)
    run = p.add_run(text)

    if level == 1:
        run.font.size = Pt(24)
        run.font.color.rgb = RGBColor(99, 102, 241)  # Accent color
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(12)
    elif level == 2:
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(60, 60, 60)
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
    elif level == 3:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(80, 80, 80)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
    else:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(100, 100, 100)

    return p

def add_styled_table(doc, rows):
    """Add a nicely formatted table"""
    if not rows:
        return

    cols = len([c.strip() for c in rows[0].split('|') if c.strip()])
    if cols == 0:
        return

    table = doc.add_table(rows=len(rows), cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Style the table
    table.style = 'Table Grid'

    for row_idx, row_data in enumerate(rows):
        cells = [c.strip() for c in row_data.split('|') if c.strip()]
        for col_idx, cell_text in enumerate(cells[:cols]):
            cell = table.rows[row_idx].cells[col_idx]
            cell.text = cell_text

            # Style header row
            if row_idx == 0:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                # Header background
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:fill'), '6366F1')  # Accent color
                shd.set(qn('w:val'), 'clear')
                tcPr.append(shd)
            else:
                # Alternating row colors
                if row_idx % 2 == 0:
                    tc = cell._tc
                    tcPr = tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:fill'), 'F8F8F8')
                    shd.set(qn('w:val'), 'clear')
                    tcPr.append(shd)

def process_markdown(content):
    """Process markdown content and return structured data"""
    lines = content.split('\n')
    elements = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Headers
        if line.startswith('#### '):
            elements.append(('heading4', line[5:]))
        elif line.startswith('### '):
            elements.append(('heading3', line[4:]))
        elif line.startswith('## '):
            elements.append(('heading2', line[3:]))
        elif line.startswith('# '):
            elements.append(('heading1', line[2:]))

        # Code block
        elif line.strip().startswith('```'):
            code_lines = []
            language = line.strip()[3:].strip()  # Get language
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            elements.append(('code', '\n'.join(code_lines), language))

        # Table
        elif line.strip().startswith('|') and i + 1 < len(lines) and '---' in lines[i + 1]:
            table_rows = [line]
            i += 1  # skip ---
            while i < len(lines) and lines[i].strip().startswith('|'):
                if '---' not in lines[i]:
                    table_rows.append(lines[i])
                i += 1
            elements.append(('table', table_rows))
            continue

        # Table without separator detection
        elif line.strip().startswith('|'):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|') and '---' not in lines[i]:
                table_rows.append(lines[i])
                i += 1
            if table_rows:
                elements.append(('table', table_rows))
                continue

        # Unordered list
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            elements.append(('ul', line.strip()[2:]))

        # Ordered list
        elif re.match(r'^\d+\. ', line.strip()):
            match = re.match(r'^(\d+)\. (.+)', line.strip())
            if match:
                elements.append(('ol', match.group(2)))

        # Horizontal rule
        elif line.strip() in ['---', '***', '___']:
            elements.append(('hr',))

        # Empty line
        elif line.strip() == '':
            elements.append(('empty',))

        # Regular paragraph
        elif line.strip():
            elements.append(('para', line))

        i += 1

    return elements

@app.post("/api/tools/md-to-word")
def md_to_word(request: MDToWordRequest):
    """Convert multiple MD files to Word document with beautiful formatting"""

    doc = Document()

    # Document properties
    doc.core_properties.title = request.title

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3)
        section.right_margin = Cm(3)

    # Title page style
    title = doc.add_heading(level=0)
    title_run = title.add_run(request.title)
    title_run.font.size = Pt(32)
    title_run.font.color.rgb = RGBColor(99, 102, 241)
    title_run.font.bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(30)

    # Subtitle with date
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    from datetime import datetime
    date_run = subtitle.add_run(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    date_run.font.size = Pt(11)
    date_run.font.color.rgb = RGBColor(150, 150, 150)
    date_run.font.italic = True

    doc.add_paragraph()  # Spacer

    for file_info in request.files:
        filename = file_info.name
        content = file_info.content

        # File title
        file_title = doc.add_heading(level=1)
        file_run = file_title.add_run(f"📄 {filename.replace('.md', '')}")
        file_run.font.size = Pt(20)
        file_run.font.color.rgb = RGBColor(60, 60, 60)
        file_title.paragraph_format.space_before = Pt(20)
        file_title.paragraph_format.space_after = Pt(15)

        elements = process_markdown(content)

        for elem in elements:
            if elem[0] == 'heading1':
                add_styled_heading(doc, elem[1], 1)
            elif elem[0] == 'heading2':
                add_styled_heading(doc, elem[1], 2)
            elif elem[0] == 'heading3':
                add_styled_heading(doc, elem[1], 3)
            elif elem[0] == 'heading4':
                add_styled_heading(doc, elem[1], 4)
            elif elem[0] == 'code':
                add_code_block(doc, elem[1], elem[2])
            elif elem[0] == 'table':
                add_styled_table(doc, elem[1])
            elif elem[0] == 'ul':
                p = doc.add_paragraph(style='List Bullet')
                run = p.add_run(elem[1])
                run.font.size = Pt(11)
            elif elem[0] == 'ol':
                p = doc.add_paragraph(style='List Number')
                run = p.add_run(elem[1])
                run.font.size = Pt(11)
            elif elem[0] == 'hr':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(15)
                p.paragraph_format.space_after = Pt(15)
                run = p.add_run('─' * 70)
                run.font.color.rgb = RGBColor(200, 200, 200)
            elif elem[0] == 'empty':
                doc.add_paragraph()
            elif elem[0] == 'para':
                p = doc.add_paragraph()
                run = p.add_run(elem[1])
                run.font.size = Pt(11)
                p.paragraph_format.space_after = Pt(6)

        # Page break between files
        if len(request.files) > 1:
            doc.add_page_break()

    # Save
    doc_buffer = io.BytesIO()
    doc.save(doc_buffer)
    doc_buffer.seek(0)

    return Response(
        content=doc_buffer.getvalue(),
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={'Content-Disposition': f'attachment; filename="{request.title}.docx"'}
    )

@app.get("/health")
def health():
    return {"status": "ok", "service": "md-to-word"}

if __name__ == "__main__":
    print("Starting MD to Word server on port 8001 with enhanced formatting...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="error")
