import re
from typing import Tuple, Optional
from db.models import DocumentType


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF file
    """
    try:
        import PyPDF2
        
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        # If no text extracted (scanned PDF), try OCR on images
        if not text.strip():
            try:
                from pdf2image import convert_from_path
                import pytesseract
                
                # Convert PDF pages to images
                images = convert_from_path(pdf_path, first_page=1, last_page=3)  # Process first 3 pages
                
                for image in images:
                    text += pytesseract.image_to_string(image) + "\n"
            except Exception as e:
                print(f"PDF OCR error: {e}")
                text = "[PDF OCR not available]"
        
        return text.strip()
    
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return "[PDF text extraction failed]"


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image using OCR
    
    Uses EasyOCR or pytesseract for text extraction.
    Falls back to dummy text if OCR libraries are not available.
    """
    try:
        # Try using EasyOCR (preferred)
        try:
            import easyocr
            reader = easyocr.Reader(['en'])
            result = reader.readtext(image_path)
            extracted_text = ' '.join([text[1] for text in result])
            return extracted_text
        except ImportError:
            pass
        
        # Try using pytesseract as fallback
        try:
            import pytesseract
            from PIL import Image
            image = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text
        except ImportError:
            pass
        
        # If no OCR library available, return placeholder
        return f"[OCR not available - document uploaded from {image_path}]"
    
    except Exception as e:
        print(f"OCR extraction error: {e}")
        return "[Text extraction failed]"


def detect_document_type(extracted_text: str) -> DocumentType:
    """
    Detect document type from extracted text
    """
    if not extracted_text or len(extracted_text) < 10:
        return DocumentType.OTHER
    
    text_upper = extracted_text.upper()
    
    # Aadhaar detection
    # Look for "Government of India" and 12 digit number pattern
    if "GOVERNMENT OF INDIA" in text_upper or "AADHAAR" in text_upper or "UIDAI" in text_upper:
        # Check for 12 digit pattern
        aadhaar_pattern = r'\d{4}\s?\d{4}\s?\d{4}'
        if re.search(aadhaar_pattern, extracted_text):
            return DocumentType.AADHAAR
    
    # PAN detection
    # Look for PAN pattern: 5 letters, 4 digits, 1 letter
    pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
    if re.search(pan_pattern, extracted_text):
        if "INCOME TAX" in text_upper or "PERMANENT ACCOUNT NUMBER" in text_upper:
            return DocumentType.PAN
    
    return DocumentType.OTHER


def extract_aadhaar_number(extracted_text: str) -> Optional[str]:
    """Extract Aadhaar number from text"""
    pattern = r'\d{4}\s?\d{4}\s?\d{4}'
    match = re.search(pattern, extracted_text)
    return match.group(0) if match else None


def extract_pan_number(extracted_text: str) -> Optional[str]:
    """Extract PAN number from text"""
    pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
    match = re.search(pattern, extracted_text)
    return match.group(0) if match else None


def validate_aadhaar(extracted_text: str) -> bool:
    """
    Validate if the document is an Aadhaar card
    Checks for Aadhaar number pattern and keywords
    """
    if not extracted_text or len(extracted_text) < 10:
        return False
    
    # Remove special characters and extra spaces for better matching
    text_normalized = re.sub(r'[^A-Za-z0-9\s]', '', extracted_text)
    text_upper = text_normalized.upper()
    
    # Check for Aadhaar keywords (more flexible)
    has_keywords = (
        "AADHAAR" in text_upper or 
        "AADHAR" in text_upper or 
        "UIDAI" in text_upper or
        ("GOVERNMENT" in text_upper and "INDIA" in text_upper) or
        "UNIQUE IDENTIFICATION" in text_upper or
        "DOB" in text_upper  # Date of Birth is common in Aadhaar
    )
    
    # Check for 12 digit Aadhaar number pattern (with or without spaces)
    # Pattern: XXXX XXXX XXXX or XXXXXXXXXXXX
    aadhaar_pattern = r'\d{4}\s?\d{4}\s?\d{4}'
    has_number = bool(re.search(aadhaar_pattern, extracted_text))
    
    # Also check for VID pattern (16 digits) which is also valid
    vid_pattern = r'\d{4}\s?\d{4}\s?\d{4}\s?\d{4}'
    has_vid = bool(re.search(vid_pattern, extracted_text))
    
    return has_keywords and (has_number or has_vid)


def validate_pan(extracted_text: str) -> bool:
    """
    Validate if the document is a PAN card
    Checks for PAN number pattern (5 letters + 4 digits + 1 letter)
    """
    if not extracted_text or len(extracted_text) < 10:
        return False
    
    # Remove special characters for better matching
    text_normalized = re.sub(r'[^A-Za-z0-9\s]', '', extracted_text)
    text_upper = text_normalized.upper()
    
    # Check for PAN pattern (more flexible)
    # Standard: ABCDE1234F (5 letters + 4 digits + 1 letter)
    pan_pattern = r'[A-Z]{5}\s?[0-9]{4}\s?[A-Z]{1}'
    has_pan_number = bool(re.search(pan_pattern, text_upper))
    
    # Check for PAN keywords (optional but helps)
    has_keywords = (
        "INCOME TAX" in text_upper or 
        "PAN" in text_upper or 
        "PERMANENT ACCOUNT" in text_upper or
        ("GOVT" in text_upper and "INDIA" in text_upper) or
        "DEPARTMENT" in text_upper
    )
    
    # PAN number is mandatory, keywords help but not required
    return has_pan_number


def validate_voter_id(extracted_text: str) -> bool:
    """
    Validate if the document is a Voter ID
    Checks for Voter ID keywords and patterns
    """
    if not extracted_text or len(extracted_text) < 10:
        return False
    
    # Remove special characters for better matching
    text_normalized = re.sub(r'[^A-Za-z0-9\s]', '', extracted_text)
    text_upper = text_normalized.upper()
    
    # Check for Voter ID keywords
    has_keywords = (
        "ELECTION" in text_upper or
        "VOTER" in text_upper or
        "ELECTOR" in text_upper or
        "ELECTORAL" in text_upper or
        "ECI" in text_upper or
        ("AGE" in text_upper and "SEX" in text_upper) or  # Common voter ID fields
        "PHOTO IDENTITY CARD" in text_upper
    )
    
    # Check for voter ID pattern (varies by state)
    # Common patterns: ABC1234567 (3 letters + 7 digits)
    voter_id_pattern = r'[A-Z]{3}\s?\d{7}'
    has_voter_id = bool(re.search(voter_id_pattern, text_upper))
    
    # Either keywords or pattern should match
    return has_keywords or has_voter_id
