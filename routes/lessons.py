from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import json

from database import get_db
from models import User, Progress
from schemas import ProgressUpdate
from dependencies import get_current_user
from services.ai_service import ai_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def load_curriculum():
    with open("data/curriculum.json", "r", encoding="utf-8") as f:
        return json.load(f)


def find_lesson(curriculum, lesson_id):
    for module in curriculum["modules"]:
        for lesson in module["lessons"]:
            if lesson["id"] == lesson_id:
                return lesson, module
    return None, None


def get_all_lessons_flat(curriculum):
    flat = []
    for module in curriculum["modules"]:
        for lesson in module["lessons"]:
            flat.append({
                "lesson": lesson,
                "module_id": module["id"],
                "module_title": module["title"]
            })
    return flat


@router.get("/lesson/{lesson_id}", response_class=HTMLResponse)
async def lesson_page(
    lesson_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    curriculum = load_curriculum()
    lesson, module = find_lesson(curriculum, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found!")

    flat_lessons = get_all_lessons_flat(curriculum)
    current_index = next(
        (i for i, item in enumerate(flat_lessons) if item["lesson"]["id"] == lesson_id),
        -1
    )

    prev_lesson = flat_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = flat_lessons[current_index + 1] if current_index < len(flat_lessons) - 1 else None

    progress = db.query(Progress).filter(
        Progress.user_id == user.id,
        Progress.lesson_id == lesson_id
    ).first()

    is_completed = progress.completed if progress else False

    completed_ids = {
        p.lesson_id for p in db.query(Progress).filter(
            Progress.user_id == user.id,
            Progress.completed == True
        ).all()
    }

    sidebar_modules = []
    for mod in curriculum["modules"]:
        sidebar_modules.append({
            "id": mod["id"],
            "title": mod["title"],
            "icon": mod["icon"],
            "lessons": [
                {
                    "id": l["id"],
                    "title": l["title"],
                    "completed": l["id"] in completed_ids
                }
                for l in mod["lessons"]
            ]
        })

    return templates.TemplateResponse(
        "pages/lesson.html",
        {
            "request": request,
            "user": user,
            "lesson": lesson,
            "module": module,
            "is_completed": is_completed,
            "prev_lesson": prev_lesson,
            "next_lesson": next_lesson,
            "sidebar_modules": sidebar_modules,
            "current_lesson_id": lesson_id
        }
    )


@router.post("/api/lesson/run-prompt")
async def run_prompt(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    body = await request.json()
    prompt = body.get("prompt", "")

    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty!")

    result = await ai_service.chat(prompt)

    if result.get("coming_soon"):
        return {"success": False, "coming_soon": True}

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return {"success": True, "response": result["reply"]}


@router.post("/api/lesson/grade-prompt")
async def grade_prompt(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    body = await request.json()
    prompt = body.get("prompt", "")

    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty!")

    result = await ai_service.grade_prompt(prompt)

    if result.get("coming_soon"):
        return {"success": False, "coming_soon": True}

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return {"success": True, "grade": result["data"]}


@router.post("/api/lesson/complete")
async def complete_lesson(
    data: ProgressUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    existing = db.query(Progress).filter(
        Progress.user_id == user.id,
        Progress.lesson_id == data.lesson_id
    ).first()

    if existing and existing.completed:
        return {"success": True, "message": "Already completed!", "xp_earned": 0}

    if existing:
        existing.completed = True
        existing.completed_at = datetime.utcnow()
        existing.xp_earned = data.xp_earned
    else:
        progress = Progress(
            user_id=user.id,
            lesson_id=data.lesson_id,
            module_id=data.module_id,
            completed=True,
            completed_at=datetime.utcnow(),
            xp_earned=data.xp_earned
        )
        db.add(progress)

    user.xp += data.xp_earned
    db.commit()

    return {
        "success": True,
        "message": "Lesson completed!",
        "xp_earned": data.xp_earned,
        "total_xp": user.xp
    }