from abc import ABC, abstractmethod
from schemas import BankStatement

class IAIExtractor(ABC):
    """
    Interface for a service that extracts data from text.
    
    """
    @abstractmethod
    def extract_data(self, 
                     text_content: str
    ) -> BankStatement:
        pass