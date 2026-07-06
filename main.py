from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from config import settings
from dependencies import get_current_user_optional

from routes import auth, dashboard, lessons, quiz, leaderboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)
app.mount("/static", StaticFiles(directory="static"), name="static")

_env = Environment(loader=FileSystemLoader("templates"))
_env.cache = None
templates = Jinja2Templates(env=_env)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(lessons.router)
app.include_router(quiz.router)
app.include_router(leaderboard.router)


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    return templates.TemplateResponse(
        request=request,
        name="pages/landing.html",
        context={"user": user, "app_name": settings.APP_NAME, "tagline": settings.TAGLINE, "charge_amount": settings.CHARGE_AMOUNT}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)