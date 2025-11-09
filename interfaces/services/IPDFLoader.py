from abc import ABC, abstractmethod

class IPDFLoader(ABC):
    """
    Interface for a service that loads text from PDF bytes.
    
    """
    @abstractmethod
    def load_text(self, 
                  file_bytes: bytes
    ) -> str:
        pass