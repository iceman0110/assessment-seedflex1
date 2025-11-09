import os
import uvicorn
from dotenv import load_dotenv
from schemas import APIResponse
from graph.nodes import GraphNodes
from graph.workflow import GraphWorkflow
from graph.processor import StatementProcessor
from services.PDFLoader import PdfLoaderService
from services.AIExtractor import AIExtractorService
from fastapi import FastAPI, UploadFile, File, HTTPException

load_dotenv()

def app_main():
    """
    Builds and returns the fully configured StatementProcessor.
    This code runs ONCE on startup. It builds and connects all 
    our classes based on the clean architecture.

    """
    provider = os.getenv("AI_PROVIDER", "google").lower()
    pdf_service = PdfLoaderService()
    ai_service = AIExtractorService(provider=provider)
    
    graph_nodes = GraphNodes(
        pdf_loader=pdf_service,
        llm_extractor=ai_service
    )
    
    workflow_builder = GraphWorkflow(nodes=graph_nodes)
    compiled_graph_app = workflow_builder.build()
    
    return StatementProcessor(graph_app=compiled_graph_app)
    
app = FastAPI(
    title="StatementSense API",
    description="Processes a ZIP file of bank statements using AI."
)

statement_processor = app_main()

# POST Method to process statement
@app.post("/process-statements/", response_model=APIResponse)
async def process_statements_endpoint(file: UploadFile = File(..., description="A .zip file containing PDF bank statements.")
):
    """
    This endpoint accepts a .zip file, processes each PDF inside
    asynchronously, and returns a single JSON summary.
    
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .zip file.")

    # Read the file bytes
    zip_bytes = await file.read()
    response = await statement_processor.process_zip_file(zip_bytes)
    
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)