from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
import json as json_lib

from database import get_db
from models import User, Progress, QuizResult
from dependencies import get_current_user
from services.certificate_service import certificate_service

router = APIRouter()

_env = Environment(loader=FileSystemLoader("templates"))
_env.cache = None
templates = Jinja2Templates(env=_env)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    with open("data/curriculum.json", "r", encoding="utf-8") as f:
        curriculum = json_lib.load(f)

    completed_lessons = db.query(Progress).filter(
        Progress.user_id == user.id,
        Progress.completed == True
    ).all()

    completed_lesson_ids = {p.lesson_id for p in completed_lessons}
    total_lessons = sum(len(module["lessons"]) for module in curriculum["modules"])

    modules_progress = []
    for module in curriculum["modules"]:
        module_lessons = module["lessons"]
        completed_count = sum(1 for lesson in module_lessons if lesson["id"] in completed_lesson_ids)
        modules_progress.append({
            "id": module["lessons"][0]["id"] if module["lessons"] else module["id"],
            "title": module["title"],
            "icon": module["icon"],
            "total": len(module_lessons),
            "completed": completed_count,
            "percent": int((completed_count / len(module_lessons)) * 100) if module_lessons else 0
        })

    overall_percent = int((len(completed_lesson_ids) / total_lessons) * 100) if total_lessons else 0

    recent_quizzes = db.query(QuizResult).filter(
        QuizResult.user_id == user.id
    ).order_by(QuizResult.created_at.desc()).limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="pages/dashboard.html",
        context={
            "user": user,
            "modules_progress": modules_progress,
            "completed_count": len(completed_lesson_ids),
            "total_lessons": total_lessons,
            "overall_percent": overall_percent,
            "recent_quizzes": recent_quizzes
        }
    )


@router.get("/certificate")
async def get_certificate(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    with open("data/curriculum.json", "r", encoding="utf-8") as f:
        curriculum = json_lib.load(f)

    total_lessons = sum(len(module["lessons"]) for module in curriculum["modules"])
    completed_count = db.query(Progress).filter(
        Progress.user_id == user.id,
        Progress.completed == True
    ).count()

    if completed_count < total_lessons:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail=f"Complete all {total_lessons} lessons first!")

    display_name = user.name if user.name else f"Learner-{user.phone[-4:]}"
    pdf_buffer = certificate_service.generate(user_name=display_name, total_xp=user.xp)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=PromptForge_Certificate_{user.phone[-4:]}.pdf"}
    )