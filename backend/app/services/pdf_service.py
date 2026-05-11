import os
from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """
    Opens a PDF file and extracts all text content.
    Returns a combined string of all pages.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")
    
    try:
        reader = PdfReader(file_path)
        text_content = []
        
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text_content.append(extracted_text)
                
        return "\n".join(text_content)
        
    except Exception as e:
        # Re-raise with a clear message for the API layer to handle
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
