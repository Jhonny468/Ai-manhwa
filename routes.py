import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import Project, NovelDocument, StoryAnalysis
from app.services.novel_parser import extract_text, SUPPORTED
from app.services.story_analyzer import StoryAnalyzer

router = APIRouter()

@router.post("/projects")
def create_project(payload: dict, db: Session = Depends(get_db)):
    title = str(payload.get("title", "")).strip()
    if not title:
        raise HTTPException(400, "Project title is required")
    project = Project(title=title, art_style=payload.get("art_style", "korean_fantasy"))
    db.add(project); db.commit(); db.refresh(project)
    return {"id": project.id, "title": project.title, "art_style": project.art_style, "status": project.status}

@router.post("/projects/{project_id}/novels")
async def upload_novel(project_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED:
        raise HTTPException(415, "Upload a TXT, PDF or DOCX file")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit")
    os.makedirs(settings.upload_dir, exist_ok=True)
    safe_name = f"{uuid.uuid4()}{suffix}"
    path = str(Path(settings.upload_dir) / safe_name)
    with open(path, "wb") as out:
        out.write(content)
    try:
        text = extract_text(path)
    except Exception as exc:
        os.remove(path)
        raise HTTPException(422, f"Could not extract text: {exc}")
    if not text.strip():
        os.remove(path)
        raise HTTPException(422, "No readable text found. Scanned PDFs need OCR, planned for a later phase.")
    doc = NovelDocument(project_id=project_id, filename=file.filename or safe_name,
                        storage_path=path, mime_type=file.content_type or "application/octet-stream",
                        extracted_text=text, word_count=len(text.split()))
    db.add(doc); db.commit(); db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "word_count": doc.word_count, "characters": len(text)}

@router.post("/projects/{project_id}/analyze")
def analyze_novel(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    novel = db.query(NovelDocument).filter_by(project_id=project_id).order_by(NovelDocument.created_at.desc()).first()
    if not novel:
        raise HTTPException(404, "Upload a novel before analysis")
    try:
        result = StoryAnalyzer().analyze(novel.extracted_text)
    except Exception as exc:
        raise HTTPException(502, str(exc))
    record = StoryAnalysis(project_id=project_id, novel_id=novel.id,
                           result_json=result, model_name=settings.openai_text_model)
    db.add(record); db.commit(); db.refresh(record)
    project.status = "analyzed"; db.commit()
    return {"analysis_id": record.id, "result": result}

@router.get("/projects/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return {"id": project.id, "title": project.title, "art_style": project.art_style,
            "status": project.status, "novels": [{"id": n.id, "filename": n.filename, "word_count": n.word_count} for n in project.novels]}
