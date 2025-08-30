from app.core.supabase_client import supabase
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.services.ingestion_service import IngestionService
from app.services.search_service import SearchService
from app.services.context_repository import ContextRepository

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/health")
def db_test():
    try:
        response = supabase.table("contexts").select("*").execute()
        print("Connection successful!")
        print(response.data)
        return {"message": "DB connection successful!"}
    except Exception as e:
        print(f"Connection failed: {e}")
        return {"message": "DB connection failed"}

@app.post("/ingest")
async def ingest_context(
    contenthtml: UploadFile = Form(...),
    user_id: str = Form(...),
    file_name: str | None = Form(None)
):
    """Ingest HTML content and process it for semantic search"""
    try:        
        if not contenthtml.content_type or "html" not in contenthtml.content_type.lower():
            raise HTTPException(status_code=400, detail="File must be HTML")
        
        ingestion_service = IngestionService()
        result = await ingestion_service.ingest_html_content(
            contenthtml=contenthtml,
            user_id=user_id,
            file_name=file_name
        )
        
        return result
        
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/search")
async def search_context(query: str, user_id: str, top_k: int = 5, threshold: float = 0.3):
    """Search for contexts using semantic similarity"""
    try:
        search_service = SearchService()
        results = await search_service.semantic_search(
            query=query, 
            user_id=user_id, 
            top_k=top_k, 
            similarity_threshold=threshold
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/context")
async def delete_context(context_id: str, user_id: str):
    """Delete a context and all related data"""
    try:
        context_repo = ContextRepository()
        
        # Verify the context exists
        context_result = context_repo.get_context_by_id(context_id)
        if not context_result.data:
            raise HTTPException(status_code=404, detail="Context not found")

        # Check user ownership
        context = context_result.data[0]
        if context.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete the context (CASCADE will handle related data)
        delete_result = context_repo.delete_context(context_id)
        if not delete_result.data:
            raise HTTPException(status_code=500, detail="Failed to delete context")
        
        return {"success": True, "message": f"Context {context_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)