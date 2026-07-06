from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


# ── Auth Schemas ──────────────────────────────────────
class PhoneRequest(BaseModel):
    phone: str

    @validator("phone")
    def validate_phone(cls, v):
        # Remove spaces
        v = v.strip().replace(" ", "")

        # Add country code if not present
        if v.startswith("016") or v.startswith("018"):
            v = "880" + v[1:]

        # Check valid prefix
        if not (v.startswith("88016") or v.startswith("88018")):
            raise ValueError("শুধুমাত্র Robi (018) এবং Airtel (016) নম্বর সাপোর্টেড!")

        # Check length
        if len(v) != 13:
            raise ValueError("Invalid phone number!")

        return v


class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str
    reference_no: Optional[str] = None

    @validator("otp")
    def validate_otp(cls, v):
        if len(v) != 6:
            raise ValueError("OTP must be 6 digits!")
        if not v.isdigit():
            raise ValueError("OTP must be numeric!")
        return v


class NameUpdateRequest(BaseModel):
    name: str

    @validator("name")
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError("Name too short!")
        if len(v) > 50:
            raise ValueError("Name too long!")
        return v.strip()


# ── User Schemas ──────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    phone: str
    name: Optional[str]
    is_verified: bool
    is_premium: bool
    xp: int
    streak: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Progress Schemas ──────────────────────────────────
class ProgressUpdate(BaseModel):
    lesson_id: str
    module_id: str
    xp_earned: int = 10


class QuizSubmit(BaseModel):
    quiz_id: str
    module_id: str
    answers: list[int]  # Selected option indexes


# ── Token Schemas ─────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── OTP Response ──────────────────────────────────────
class OTPResponse(BaseModel):
    success: bool
    message: str
    reference_no: Optional[str] = None
    demo_mode: bool = False