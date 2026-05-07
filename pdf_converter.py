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


def describe_image_free(image_bytes: bytes) -> str:
    """
    Use Hugging Face free inference API to describe image
    Model: Salesforce/blip-image-captioning-large (completely free)
    """
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/octet-stream"},
            data=image_bytes,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'Diagram or flowchart present')
        
        return "Diagram or flowchart present"
        
    except Exception:
        return "Visual content present"
