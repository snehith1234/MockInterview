import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.resume_parser import extract_text

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx")


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only PDF and Word (.doc, .docx) resumes are supported.")

    safe_filename = file.filename.replace("/", "_").replace("\\", "_")
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text(file_path)
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from this file.")

    return {
        "filename": safe_filename,
        "resume_text": resume_text,
    }
