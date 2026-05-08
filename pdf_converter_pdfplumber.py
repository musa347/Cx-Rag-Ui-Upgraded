"""
PDF to Markdown converter using pdfplumber
Pure Python, better text extraction than PyPDF2
"""

import pdfplumber
import io
from typing import Tuple

def convert_pdf_to_markdown(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Convert PDF to markdown with better text extraction
    Returns: (markdown_content, num_diagrams)
    """
    markdown_content = []
    diagram_count = 0
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            markdown_content.append(f"\n## Page {page_num + 1}\n")
            
            # Extract text (better than PyPDF2)
            text = page.extract_text()
            if text:
                markdown_content.append(text)
            
            # Extract tables
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    markdown_content.append("\n**Table:**\n")
                    for row in table:
                        markdown_content.append("| " + " | ".join(str(cell) if cell else "" for cell in row) + " |")
                    markdown_content.append("\n")
            
            # Detect images
            if page.images:
                for img in page.images:
                    diagram_count += 1
                    markdown_content.append(f"\n**[Diagram {diagram_count} present on this page]**\n")
    
    return '\n'.join(markdown_content), diagram_count
