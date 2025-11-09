from pydantic import BaseModel, Field
from typing import List, Union, Literal

# Bank Statement Schemas
class BankStatement(BaseModel):
    """
    Extracted financial data from a single bank statement.
    
    """
    statement_period: str = Field(
        ..., 
        description="The start and end date of the statement, e.g., 'Jan 1, 2024 - Jan 31, 2024'"
    )
    total_credits: float = Field(
        ..., 
        description="The total amount of all credits/deposits."
    )
    total_debits: float = Field(
        ..., 
        description="The total amount of all debits/withdrawals."
    )


class FileProcessSuccess(BaseModel):
    """
    Represents a single PDF that was processed successfully.
    
    """
    file_name: str
    status: Literal["processed"] = "processed"
    data: BankStatement

class FileProcessFail(BaseModel):
    """
    Represents a single PDF that failed to process.
    
    """
    file_name: str
    status: Literal["failed"] = "failed"
    error: str

class Summary(BaseModel):
    """
    The top-level summary for the entire batch.
    
    """
    grand_total_credits: float
    grand_total_debits: float
    total_files_processed: int
    total_files_failed: int

class APIResponse(BaseModel):
    """
    The final, complete JSON response for the API.
    
    """
    summary: Summary
    files: List[Union[FileProcessSuccess, FileProcessFail]]