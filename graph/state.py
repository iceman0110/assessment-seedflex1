from typing import TypedDict, Optional, Union
from schemas import BankStatement, FileProcessSuccess, FileProcessFail

class GraphState(TypedDict):
    """
    Defines the data structure that flows through the graph.
    This is the internal, private "memory" of the workflow.
    
    """
    file_name: str
    file_content: bytes
    pdf_text: Optional[str]
    extracted_data: Optional[BankStatement]
    error: Optional[str]
    final_result: Optional[Union[FileProcessSuccess, FileProcessFail]]