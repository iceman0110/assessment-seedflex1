import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from schemas import BankStatement
from interfaces.services.IAIExtractor import IAIExtractor

class AIExtractorService(IAIExtractor):
    """
    Implementation of IAIExtractor that can be configured
    for different AI providers (e.g., OpenAI, Google).
    """
    
    def __init__(self, 
                 provider: str, 
                 model_name: str = None
    ):
        self.model = self._create_model(provider, model_name)
        
        # This part is generic and works with any LangChain-compatible model
        structured_llm = self.model.with_structured_output(BankStatement)
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert financial assistant. Extract the required fields from the following bank statement text."),
            ("user", "{pdf_text}")
        ])
        
        self.chain = prompt | structured_llm

    def _create_model(self, 
                      provider: str, 
                      model_name: str = None
    ) -> BaseChatModel:
        """
        Private helper to instantiate the correct model.
        
        """
        if provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables.")
            
            return ChatGoogleGenerativeAI(
                model=model_name or "gemini-2.5-pro",
                google_api_key=api_key,
                temperature=0
            )
            
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")
                
            return ChatOpenAI(
                model=model_name or "gpt-4o",
                openai_api_key=api_key,
                temperature=0
            )
            
        else:
            raise ValueError(f"Unsupported AI provider: '{provider}'. Supported: 'openai', 'google'.")

    def extract_data(self, 
                     text_content: str
    ) -> BankStatement:
        """
        Extracts data using the pre-configured chain.
        
        """
        try:
            return self.chain.invoke({"pdf_text": text_content})
        
        except Exception as e:
            # The error will now clearly state which provider failed
            raise Exception(f"LLM ({self.model.__class__.__name__}) failed to extract fields: {str(e)}")