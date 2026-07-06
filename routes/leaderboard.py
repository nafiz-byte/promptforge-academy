from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from models import User
from dependencies import get_current_user

router = APIRouter()

_env = Environment(loader=FileSystemLoader("templates"))
_env.cache = None
templates = Jinja2Templates(env=_env)


@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    top_users = db.query(User).filter(
        User.is_premium == True
    ).order_by(desc(User.xp)).limit(50).all()

    all_users_ranked = db.query(User).filter(
        User.is_premium == True
    ).order_by(desc(User.xp)).all()

    user_rank = next(
        (i + 1 for i, u in enumerate(all_users_ranked) if u.id == user.id),
        None
    )

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
        request=request,
        name="pages/leaderboard.html",
        context={
            "user": user,
            "leaderboard": leaderboard_data,
            "user_rank": user_rank
        }
    )