from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from services.jwt_service import get_user_id_from_token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Cookie থেকে token নিয়ে user বের করে।
    Protected routes এ এটা ব্যবহার হবে।
    """
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated!")

    user_id = get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token!")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found!")

    if not user.is_premium:
        raise HTTPException(status_code=403, detail="Premium access required!")

    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    """
    Login page এ check করতে — error না দিয়ে None return করে
    """
    token = request.cookies.get("access_token")

    if not token:
        return None

    user_id = get_user_id_from_token(token)

    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user