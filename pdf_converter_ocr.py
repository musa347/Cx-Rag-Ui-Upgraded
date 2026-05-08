"""
PDF to Markdown converter with diagram descriptions
Uses: pdf2image, pytesseract, Hugging Face Inference API
"""

from pdf2image import convert_from_bytes
import pytesseract
import requests
import io
from typing import Tuple

def convert_pdf_to_markdown(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Convert PDF to markdown with diagram descriptions using OCR
    Returns: (markdown_content, num_diagrams)
    """
    # Convert PDF pages to images
    images = convert_from_bytes(pdf_bytes, dpi=200)
    
    markdown_content = []
    diagram_count = 0
    
    for page_num, image in enumerate(images):
        markdown_content.append(f"\n## Page {page_num + 1}\n")
        
        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        
        if text.strip():
            markdown_content.append(text)
        
        # Convert image to bytes for AI description
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Try to get AI description of the page (includes diagrams)
        try:
            description = describe_image_free(img_byte_arr)
            if description and "diagram" in description.lower():
                markdown_content.append(f"\n**Diagram {diagram_count + 1}:** {description}\n")
                diagram_count += 1
        except:
            pass
    
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
