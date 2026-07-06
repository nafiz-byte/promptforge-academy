from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json

from database import get_db
from models import User, QuizResult, Progress
from schemas import QuizSubmit
from dependencies import get_current_user

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


@router.get("/quiz/{lesson_id}", response_class=HTMLResponse)
async def quiz_page(
    lesson_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    curriculum = load_curriculum()
    lesson, module = find_lesson(curriculum, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found!")

    quiz_questions = lesson.get("quiz", [])

    if not quiz_questions:
        raise HTTPException(status_code=404, detail="No quiz available for this lesson!")

    # Remove correct answers from frontend data (security)
    safe_questions = [
        {"question": q["question"], "options": q["options"]}
        for q in quiz_questions
    ]

    # Check previous attempts
    previous_result = db.query(QuizResult).filter(
        QuizResult.user_id == user.id,
        QuizResult.quiz_id == lesson_id
    ).order_by(QuizResult.created_at.desc()).first()

    return templates.TemplateResponse(
        "pages/quiz.html",
        {
            "request": request,
            "user": user,
            "lesson": lesson,
            "module": module,
            "questions": safe_questions,
            "total_questions": len(safe_questions),
            "previous_result": previous_result
        }
    )


@router.post("/api/quiz/submit")
async def submit_quiz(
    data: QuizSubmit,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    curriculum = load_curriculum()
    lesson, module = find_lesson(curriculum, data.quiz_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="Quiz not found!")

    quiz_questions = lesson.get("quiz", [])

    if len(data.answers) != len(quiz_questions):
        raise HTTPException(status_code=400, detail="Answer count mismatch!")

    # Calculate score
    score = 0
    results = []
    for i, question in enumerate(quiz_questions):
        is_correct = data.answers[i] == question["correct"]
        if is_correct:
            score += 1
        results.append({
            "question": question["question"],
            "your_answer": data.answers[i],
            "correct_answer": question["correct"],
            "is_correct": is_correct,
            "options": question["options"]
        })

    total = len(quiz_questions)
    percent = int((score / total) * 100) if total else 0
    passed = percent >= 60  # 60% to pass

    xp_earned = score * 10 if passed else score * 5

    # Save result
    quiz_result = QuizResult(
        user_id=user.id,
        quiz_id=data.quiz_id,
        module_id=data.module_id,
        score=score,
        total=total,
        passed=passed,
        xp_earned=xp_earned
    )
    db.add(quiz_result)

    # Award XP
    user.xp += xp_earned

    db.commit()

    return {
        "success": True,
        "score": score,
        "total": total,
        "percent": percent,
        "passed": passed,
        "xp_earned": xp_earned,
        "total_xp": user.xp,
        "results": results
    }