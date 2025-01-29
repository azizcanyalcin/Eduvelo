import asyncio
import io
import json
import PyPDF2
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

from RnD.GenerateQuizFromPaper import generate_quiz_from_paper
from RnD.ResearchPaper import extract_paper_gpt
from firebase.auth import sign_up, sign_in
from firebase.storage import upload_file
from models import SignUpRequest
from utils.PDFToQuizPipeline import PDFQuizPipeline
from utils.PDFProcessor import PDFProcessor

app = FastAPI()

API_KEY = "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"

pipeline = PDFQuizPipeline(api_key=API_KEY)

quizzes = []

async def save_file_async(file, path):
    loop = asyncio.get_running_loop()
    with open(path, "wb") as temp_file:
        await loop.run_in_executor(None, shutil.copyfileobj, file.file, temp_file)

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file.filename

    await save_file_async(file, temp_file_path)

    try: 
        quiz_data = pipeline.process_pdf(str(temp_file_path), max_pages=1)
        quizzes.extend(quiz_data)
        # Write quizzes to a JSON file
        with open("quizzes.json", "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)
                
        upload_file("quizzes.json", "quizzes/quiz.json")
        
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                print(f"Dosya silinemedi: {e}")

@app.get("/get-quizzes/")
async def get_quizzes():
    return JSONResponse(content={"quizzes": quizzes})

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
