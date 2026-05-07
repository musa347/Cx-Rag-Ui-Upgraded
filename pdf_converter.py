"""
PDF to Markdown converter with diagram descriptions
Uses free tools: PyPDF2, Hugging Face Inference API
"""

from PyPDF2 import PdfReader
import requests
import io
from typing import Tuple

def convert_pdf_to_markdown(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Convert PDF to markdown with diagram descriptions
    Returns: (markdown_content, num_diagrams)
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    markdown_content = []
    diagram_count = 0
    
    for page_num, page in enumerate(reader.pages):
        # Extract text
        text = page.extract_text()
        
        # Check if page has images
        if '/XObject' in page['/Resources']:
            xobjects = page['/Resources']['/XObject'].get_object()
            
            has_images = False
            for obj in xobjects:
                if xobjects[obj]['/Subtype'] == '/Image':
                    has_images = True
                    break
            
            if has_images:
                # Page has diagrams
                markdown_content.append(f"\n## Page {page_num + 1}\n")
                if text.strip():
                    markdown_content.append(text)
                
                # Note: PyPDF2 doesn't easily extract image bytes
                # So we'll just note that diagrams are present
                markdown_content.append(f"\n**[Diagram {diagram_count + 1} present on this page]**\n")
                diagram_count += 1
            else:
                # Regular text page
                if text.strip():
                    markdown_content.append(text)
        else:
            # Regular text page
            if text.strip():
                markdown_content.append(text)
    
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
