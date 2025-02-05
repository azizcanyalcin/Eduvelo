import asyncio
import io
import json
import os
import time
import PyPDF2
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

from firebase.auth import sign_up, sign_in
from firebase.storage import upload_file

from models import SignUpRequest

from utils.PDFToQuizPipeline import PDFQuizPipeline
from utils.PDFProcessor import PDFProcessor
from utils.TextProcessor import TextProcessor

from utils.ImageExtractor import ImageExtractor


load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)
API_KEY = os.getenv("OPENAI_API_KEY")

pipeline = PDFQuizPipeline(api_key=API_KEY)
filePath = ""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
import asyncio

app = FastAPI()

UPLOAD_DIR = "extracted_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/extract_images/")
async def extract_images(pdf: UploadFile = File(...)):
    try:
        pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)
        with open(pdf_path, "wb") as buffer:
            buffer.write(await pdf.read())

        extractor = ImageExtractor(pdf_path)

        pdfplumber_images = extractor.extract_images_pdfplumber()
        pymupdf_images = extractor.extract_images_pymupdf()

        all_images = pdfplumber_images + pymupdf_images

        return {"images": all_images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def save_file_async(file: UploadFile, file_path: Path):
    """Save the uploaded file asynchronously."""
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

async def stream_quiz_sse(pdf_path):
    """Yields quizzes as Server-Sent Events (SSE) one by one."""
    try:
        async for quiz in pipeline.pdf_to_quiz(pdf_path, max_pages=1): 
            print("Streaming quiz:", quiz)
            yield f"data: {json.dumps(quiz)}\n\n" 
            await asyncio.sleep(0.1)  
        yield "data: FINISHED\n\n"
    except Exception as e:
        print(f"Error during quiz generation: {e}")
        yield f"data: {json.dumps({'error': 'Failed to generate quiz'})}\n\n"

@app.post("/file-upload/")
async def get_file(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file.filename

    await save_file_async(file, temp_file_path)
    return temp_file_path

@app.get("/quiz-stream/")
async def sse():
    return StreamingResponse(stream_quiz_sse("temp_uploads\paper.pdf"))

def event_stream():
    while True:
        time.sleep(5)  # Simulating some processing delay
        yield f"data: {time.time()}\n\n"  # Sending current time as a message

@app.get("/events")
async def sse():
    return StreamingResponse(event_stream())


@app.post("/signup/")
async def register(request: SignUpRequest):
    sign_up(request.email, request.password)
    return JSONResponse(content={"message": "Registration successful!"})

@app.post("/login/")
async def login(request: SignUpRequest):
    sign_in(request.email, request.password)
    return JSONResponse(content={"message": "Login successful!"})


"""LangChain Implementation"""

from langchain_openai import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings


model = ChatOpenAI(model="gpt-4o-mini")

@app.get("/invoke-model/")
async def invoke_model():
    model.invoke("Hello, world!")
    return JSONResponse(content={"message": "Model Invoked!"})


async def stream_quiz_langchain(file_path):
    loader = PyPDFLoader(file_path)
    pages = []
    async for page in loader.alazy_load():
        pages.append(page)
    
    
    # # 1. PDF'den Metni Yükle
    # loader = PyPDFLoader(pdf_path)
    # documents = loader.load()

    # # 2. Metni Paragraflara Böl
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    paragraphs = text_splitter.split_documents(pages)
    
    for pharagraph in paragraphs:
        print("PARAGRAPH: " , pharagraph.page_content)
    
    # # 3. Özel Prompt Tanımla
    quiz_prompt = PromptTemplate(
        input_variables=["paragraph"],
        template="Şu paragraf için 3 soruluk çoktan seçmeli bir quiz hazırla:\n\n{paragraph}"
    )

    # # 4. LLM Zinciri Tanımla

    quiz_chain = LLMChain(llm=model, prompt=quiz_prompt)

    # # 5. Tüm Paragraflar için Quiz Üret
    quizzes = [quiz_chain.run({"paragraph": para.page_content}) for para in paragraphs]

    # 6. Sonuçları Yazdır
    for idx, quiz in enumerate(quizzes):
        print(quiz)
        yield(f"Paragraf {idx+1} için Quiz:\n{quiz}\n")
    

@app.post("/langchain-quiz-from-pdf/")
async def langchain_pdf_to_quiz(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file.filename

    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    return StreamingResponse(stream_quiz_langchain(str(temp_file_path)), media_type="application/json")

"""End of LangChain Implementation"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
