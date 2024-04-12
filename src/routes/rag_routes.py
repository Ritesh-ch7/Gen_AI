from fastapi import FastAPI, APIRouter, HTTPException, Depends, status,Header, Query,Request
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from sqlalchemy.orm import Session
from src.config.database_initializer import get_db
import pathlib
import aiofiles
from fastapi import File, UploadFile
from ..services.rag_services.rag_service import RagService
from ..services.rag_services.rag_vector_db import add_file_to_vector_store
import uuid, os
from src.config.rag_tool_db_config import create_faiss_db_directory, create_uploads_directory

router = APIRouter()

uploads_dir = pathlib.Path("uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

@router.post('/upload/pdf/{session_id}')
async def upload_file(session_id, file: UploadFile = File(...)):
    try:
        
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        if session_id == 'undefined':
            session_id = str(uuid.uuid4())

        if not os.path.exists("uploads"):
            create_uploads_directory()
            create_faiss_db_directory()

        file_name = pathlib.Path(uploads_dir, file.filename)
        async with aiofiles.open(file_name, 'wb') as f:
            contents = await file.read()  # Read the file contents
            await f.write(contents)  # Write the contents to the file
        file_path = f'uploads/{file.filename}'

        await add_file_to_vector_store(file_path, session_id)
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "session_id": session_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error uploading the file: {str(e)}")

@router.post('/query/pdf/{filename:path}/{user_id}/{session_id}')
async def query_pdf(filename: str, request: Request,session_id,user_id, db : Session = Depends(get_db)):
    data = await request.json()
    user_query = data.get('user',None)

    return await RagService(db).rag_response(user_query,user_id,session_id,filename)