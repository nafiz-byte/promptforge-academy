from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import User, OTPSession, Transaction
from schemas import PhoneRequest, OTPVerifyRequest, NameUpdateRequest
from services.otp_service import otp_service
from services.payment_service import payment_service
from services.jwt_service import create_token
from config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ── Pages ─────────────────────────────────────────────
@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )


@router.get("/verify-otp", response_class=HTMLResponse)
async def otp_page(request: Request, phone: str = ""):
    return templates.TemplateResponse(
        "auth/otp.html",
        {"request": request, "phone": phone}
    )


# ── API Endpoints ──────────────────────────────────────
@router.post("/api/auth/request-otp")
async def request_otp(
    data: PhoneRequest,
    db: Session = Depends(get_db)
):
    phone = data.phone

    result = await otp_service.request_otp(phone)

    if result["success"]:
        # Find or create user
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            user = User(phone=phone)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Save OTP session
        otp_session = OTPSession(
            phone=phone,
            reference_no=result.get("reference_no"),
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            user_id=user.id
        )
        db.add(otp_session)
        db.commit()

    return result


@router.post("/api/auth/verify-otp")
async def verify_otp(
    data: OTPVerifyRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    phone = data.phone

    # Get latest OTP session
    otp_session = db.query(OTPSession).filter(
        OTPSession.phone == phone,
        OTPSession.is_used == False
    ).order_by(OTPSession.created_at.desc()).first()

    if not otp_session:
        raise HTTPException(status_code=400, detail="OTP session not found!")

    # Check expiry
    if datetime.utcnow() > otp_session.expires_at:
        raise HTTPException(status_code=400, detail="OTP expired!")

    # Verify OTP
    verify_result = await otp_service.verify_otp(
        phone=phone,
        otp=data.otp,
        reference_no=otp_session.reference_no
    )

    if not verify_result["success"]:
        raise HTTPException(status_code=400, detail="Invalid OTP!")

    # Get user
    user = db.query(User).filter(User.phone == phone).first()

    # Charge every time — daily access model
    charge_result = await payment_service.charge_user(
        phone=phone,
        reference_no=otp_session.reference_no
    )

    if not charge_result["success"]:
        raise HTTPException(
            status_code=402,
            detail="Payment failed! Please ensure you have sufficient balance."
        )

    # Save transaction
    txn = Transaction(
        phone=phone,
        amount=float(settings.CHARGE_AMOUNT),
        status="success",
        reference_no=otp_session.reference_no,
        internal_txn_id=charge_result.get("transaction_id"),
        user_id=user.id
    )
    db.add(txn)

    # Update streak
    if user.last_active:
        diff = datetime.utcnow() - user.last_active
        if diff.days == 1:
            user.streak += 1
        elif diff.days > 1:
            user.streak = 1
    else:
        user.streak = 1

    user.is_verified = True
    user.is_premium = True
    user.last_active = datetime.utcnow()

    # Mark OTP as used
    otp_session.is_used = True
    db.commit()
    db.refresh(user)

    # Create JWT token
    token = create_token(user.id, user.phone)

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,  # 24 hours
        samesite="lax"
    )

    return {
        "success": True,
        "message": "Welcome to PromptForge Academy!",
        "token": token,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "is_premium": user.is_premium,
            "xp": user.xp
        },
        "redirect": "/dashboard"
    }


@router.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True, "redirect": "/"}


@router.post("/api/auth/update-name")
async def update_name(
    data: NameUpdateRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    from services.jwt_service import get_user_id_from_token

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized!")

    user_id = get_user_id_from_token(token)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    user.name = data.name
    db.commit()

    return {"success": True, "message": "Name updated!"}