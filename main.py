import asyncio
import io
import json
import PyPDF2
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

from firebase.auth import sign_up, sign_in
from firebase.storage import upload_file
from models import SignUpRequest
from utils.PDFToQuizPipeline import PDFQuizPipeline
from utils.PDFProcessor import PDFProcessor
from utils.TextProcessor import TextProcessor

app = FastAPI()

API_KEY = "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"

pipeline = PDFQuizPipeline(api_key=API_KEY)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
import asyncio

app = FastAPI()

async def save_file_async(file: UploadFile, file_path: Path):
    """Save the uploaded file asynchronously."""
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # Read in chunks (1MB)
            buffer.write(chunk)

async def stream_quiz(pdf_path):
    async for quiz in pipeline.pdf_to_quiz(pdf_path, max_pages=5):
        yield quiz

@app.post("/generate-quiz-from-pdf/")
async def generate_quiz_from_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file.filename

    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    return StreamingResponse(stream_quiz(str(temp_file_path)), media_type="application/json")

@app.post("/signup/")
async def register(request: SignUpRequest):
    sign_up(request.email, request.password)
    return JSONResponse(content={"message": "Registration successful!"})

@app.post("/login/")
async def login(request: SignUpRequest):
    sign_in(request.email, request.password)
    return JSONResponse(content={"message": "Login successful!"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
