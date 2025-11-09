from interfaces.services.IPDFLoader import IPDFLoader
from interfaces.services.IAIExtractor import IAIExtractor
from graph.state import GraphState
from schemas import FileProcessSuccess, FileProcessFail

class GraphNodes:
    """
    Contains all the node functions for the graph.
    It is initialized with the "tools" (services) it needs,
    based on the abstract interfaces.
    
    """
    def __init__(self, 
                 pdf_loader: IPDFLoader, 
                 llm_extractor: IAIExtractor
    ):
        self.pdf_loader = pdf_loader
        self.llm_extractor = llm_extractor

    def load_pdf(self, 
                 state: GraphState
    ) -> dict:
        """
        Node 1: Calls the PDF loader service.
        This node's job is to orchestrate and catch errors.
        """
        print(f"--- 1. Loading PDF: {state['file_name']} ---")
        try:
            text = self.pdf_loader.load_text(state["file_content"])
            return {"pdf_text": text}
        
        except Exception as e:
            return {"error": str(e)}

    def extract_data(self, 
                     state: GraphState
    ) -> dict:
        """
        Node 2: Calls the LLM extractor service.
        This node orchestrates and catches errors.
        
        """
        print(f"--- 2. Extracting data from: {state['file_name']} ---")
        try:
            # Use the injected service
            data = self.llm_extractor.extract_data(state["pdf_text"])
            return {"extracted_data": data}
        
        except Exception as e:
            return {"error": str(e)}

    def finalize_result(self, 
                        state: GraphState
    ) -> dict:
        """
        Node 3: Formats the final output for this single file.
        This node runs at the end, whether it succeeded or failed.
        
        """
        print(f"--- 3. Finalizing results for: {state['file_name']} ---")
        file_name = state["file_name"]
        
        if state.get("error"):
            result = FileProcessFail(file_name=file_name, error=state["error"])
            
        elif state.get("extracted_data"):
            result = FileProcessSuccess(file_name=file_name, data=state["extracted_data"])
            
        else:
            result = FileProcessFail(file_name=file_name, error="Unknown processing error.")
            
        return {"final_result": result}