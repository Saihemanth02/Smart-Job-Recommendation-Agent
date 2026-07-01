import os
import pdfplumber
import docx

def parse_pdf(file_path_or_bytes) -> str:
    """
    Extracts raw text from a PDF file.
    """
    text = ""
    with pdfplumber.open(file_path_or_bytes) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def parse_docx(file_path_or_bytes) -> str:
    """
    Extracts raw text from a DOCX file.
    """
    doc = docx.Document(file_path_or_bytes)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text_from_file(file_bytes, filename: str) -> str:
    """
    Checks the extension and extracts text.
    """
    ext = os.path.splitext(filename.lower())[1]
    
    # We can write file_bytes to a temporary file, or load directly from bytes if supported.
    # pdfplumber and docx can accept file-like objects (BytesIO)
    from io import BytesIO
    file_stream = BytesIO(file_bytes)
    
    if ext == ".pdf":
        return parse_pdf(file_stream)
    elif ext in [".docx", ".doc"]:
        try:
            return parse_docx(file_stream)
        except Exception as e:
            # If docx fails on older .doc files or standard docx format errors, fallback to text
            raise ValueError(f"Could not parse DOCX. Ensure format is valid: {str(e)}")
    elif ext == ".txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Please upload .pdf, .docx, or .txt")
