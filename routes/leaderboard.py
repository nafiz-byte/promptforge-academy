from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from models import User
from dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Top 50 users by XP
    top_users = db.query(User).filter(
        User.is_premium == True
    ).order_by(desc(User.xp)).limit(50).all()

    # Find current user's rank
    all_users_ranked = db.query(User).filter(
        User.is_premium == True
    ).order_by(desc(User.xp)).all()

    user_rank = next(
        (i + 1 for i, u in enumerate(all_users_ranked) if u.id == user.id),
        None
    )

    # Mask phone numbers for privacy (show only last 4 digits)
    leaderboard_data = []
    for i, u in enumerate(top_users):
        masked_phone = f"***{u.phone[-4:]}" if u.phone else "Unknown"
        display_name = u.name if u.name else f"Learner{masked_phone}"

        leaderboard_data.append({
            "rank": i + 1,
            "name": display_name,
            "xp": u.xp,
            "streak": u.streak,
            "is_current_user": u.id == user.id
        })

    return templates.TemplateResponse(
        "pages/leaderboard.html",
        {
            "request": request,
            "user": user,
            "leaderboard": leaderboard_data,
            "user_rank": user_rank
        }
    )

from fastapi.responses import StreamingResponse
from services.certificate_service import certificate_service
import json as json_lib


@router.get("/certificate")
async def get_certificate(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    with open("data/curriculum.json", "r", encoding="utf-8") as f:
        curriculum = json_lib.load(f)

    total_lessons = sum(len(module["lessons"]) for module in curriculum["modules"])

    completed_count = db.query(Progress).filter(
        Progress.user_id == user.id,
        Progress.completed == True
    ).count()

    if completed_count < total_lessons:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail=f"Complete all {total_lessons} lessons first! ({completed_count}/{total_lessons} done)"
        )

    display_name = user.name if user.name else f"Learner-{user.phone[-4:]}"

    pdf_buffer = certificate_service.generate(
        user_name=display_name,
        total_xp=user.xp
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=PromptForge_Certificate_{user.phone[-4:]}.pdf"
        }
    )