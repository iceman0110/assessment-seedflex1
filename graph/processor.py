import io
import zipfile
import asyncio
from typing import List, Union
from langgraph.pregel import Pregel
from schemas import APIResponse, FileProcessSuccess, FileProcessFail, Summary
from graph.state import GraphState

class StatementProcessor:
    """
    This class orchestrates the entire zip file processing.
    It takes the compiled graph (the "assembly line") and
    manages the process of sending each file through it.
    
    """
    def __init__(self, 
                 graph_app: Pregel
    ):
        self.graph_app = graph_app

    async def process_zip_file(self, 
                               zip_file_bytes: bytes
    ) -> APIResponse:
        """
        This is the main business logic method.
        It processes a .zip file, runs each PDF through the graph,
        and aggregates the final response.
        
        """
        zip_file = io.BytesIO(zip_file_bytes)
        tasks = []
        results: List[Union[FileProcessSuccess, FileProcessFail]] = []

        try:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                for file_name in zf.namelist():
                    # Skip metadata files and non-PDFs
                    if file_name.startswith('__MACOSX/') or not file_name.lower().endswith(".pdf"):
                        continue
                    
                    try:
                        content = zf.read(file_name)
                        initial_state = GraphState(
                            file_name=file_name,
                            file_content=content,
                            pdf_text=None,
                            extracted_data=None,
                            error=None,
                            final_result=None
                        )
                        
                        # Add the task of running the graph for this file.
                        tasks.append(
                            asyncio.to_thread(self.graph_app.invoke, initial_state)
                        )
                        
                    except Exception as e:
                        results.append(FileProcessFail(file_name=file_name, error=f"Failed to read file from zip: {str(e)}"))
            
            # Run all file processing tasks concurrently
            graph_outputs = await asyncio.gather(*tasks)
            
            # Collect the final results from each graph run
            for output_state in graph_outputs:
                results.append(output_state['final_result'])

        except zipfile.BadZipFile:
            return APIResponse(
                summary=Summary(grand_total_credits=0, grand_total_debits=0, total_files_processed=0, total_files_failed=0),
                files=[FileProcessFail(file_name="upload.zip", error="Invalid or corrupted .zip file.")]
            )

        return self._build_api_response(results)

    def _build_api_response(self, 
                            results: List[Union[FileProcessSuccess, FileProcessFail]]
    ) -> APIResponse:
        """
        Private helper to aggregate all results into the final summary.
        
        """
        grand_total_credits = 0.0
        grand_total_debits = 0.0
        total_files_processed = 0
        total_files_failed = 0
        
        for res in results:
            if isinstance(res, FileProcessSuccess):
                total_files_processed += 1
                grand_total_credits += res.data.total_credits
                grand_total_debits += res.data.total_debits
            elif isinstance(res, FileProcessFail):
                total_files_failed += 1
                
        summary_data = Summary(
            grand_total_credits=grand_total_credits,
            grand_total_debits=grand_total_debits,
            total_files_processed=total_files_processed,
            total_files_failed=total_files_failed
        )
        
        return APIResponse(summary=summary_data, files=results)