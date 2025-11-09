import io
from pypdf import PdfReader
from interfaces.services.IPDFLoader import IPDFLoader

class PdfLoaderService(IPDFLoader):
    """
    Implementation of IPdfLoader using the pypdf library.
    
    """
    
    def load_text(self, 
                  file_bytes: bytes
    ) -> str:
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text:
                raise ValueError("Could not extract any text from the PDF. It might be an image.")
                
            return text
        except Exception as e:
            raise Exception(f"Failed to read PDF file: {str(e)}")