"""
PDF to Markdown converter with diagram descriptions
Uses free tools: pypdf, Hugging Face Inference API
"""

from pypdf import PdfReader
import requests
import io
from typing import Tuple
from PIL import Image

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
        images = page.images if hasattr(page, 'images') else []
        
        if images:
            # Page has diagrams
            markdown_content.append(f"\n## Page {page_num + 1}\n")
            if text.strip():
                markdown_content.append(text)
            
            # Extract and describe each image
            for img_index, image in enumerate(images):
                try:
                    # Get image data
                    image_bytes = image.data
                    
                    # Describe using free Hugging Face API
                    description = describe_image_free(image_bytes)
                    
                    markdown_content.append(f"\n**Diagram {diagram_count + 1}:** {description}\n")
                    diagram_count += 1
                    
                except Exception as e:
                    markdown_content.append(f"\n[Diagram {diagram_count + 1} present - could not extract description]\n")
                    diagram_count += 1
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
