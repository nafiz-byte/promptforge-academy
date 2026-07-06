import httpx
import random
from datetime import datetime, timedelta
from config import settings


class OTPService:

    async def request_otp(self, phone: str) -> dict:
        """
        Demo mode: fixed OTP 123456
        Production: bdApps OTP request
        """
        if settings.DEMO_MODE:
            return await self._demo_request(phone)
        else:
            return await self._bdapps_request(phone)


    async def verify_otp(self, phone: str, otp: str, reference_no: str = None) -> dict:
        """
        Demo mode: check if OTP == 123456
        Production: bdApps OTP verify
        """
        if settings.DEMO_MODE:
            return await self._demo_verify(otp)
        else:
            return await self._bdapps_verify(reference_no, otp)


    # ── Demo Mode ─────────────────────────────────────
    async def _demo_request(self, phone: str) -> dict:
        print(f"[DEMO] OTP sent to {phone}: {settings.DEMO_OTP}")
        return {
            "success": True,
            "reference_no": f"DEMO_{random.randint(100000, 999999)}",
            "message": f"OTP sent! (Demo: use {settings.DEMO_OTP})",
            "demo_mode": True
        }

    async def _demo_verify(self, otp: str) -> dict:
        if otp == settings.DEMO_OTP:
            return {
                "success": True,
                "message": "OTP verified successfully!",
                "demo_mode": True
            }
        return {
            "success": False,
            "message": "Invalid OTP!",
            "demo_mode": True
        }


    # ── Production Mode (bdApps) ──────────────────────
    async def _bdapps_request(self, phone: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.BDAPPS_BASE_URL}/otp/request",
                    json={
                        "applicationId": settings.BDAPPS_APP_ID,
                        "password": settings.BDAPPS_PASSWORD,
                        "subscriberId": f"tel:{phone}"
                    },
                    timeout=10.0
                )
                data = response.json()

                if data.get("statusCode") == "S1000":
                    return {
                        "success": True,
                        "reference_no": data.get("referenceNo"),
                        "message": "OTP sent to your Robi/Airtel number!",
                        "demo_mode": False
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to send OTP. Try again!",
                        "demo_mode": False
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Service unavailable: {str(e)}",
                "demo_mode": False
            }


    async def _bdapps_verify(self, reference_no: str, otp: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.BDAPPS_BASE_URL}/otp/verify",
                    json={
                        "applicationId": settings.BDAPPS_APP_ID,
                        "password": settings.BDAPPS_PASSWORD,
                        "referenceNo": reference_no,
                        "otp": otp
                    },
                    timeout=10.0
                )
                data = response.json()

                if data.get("statusCode") == "S1000":
                    return {
                        "success": True,
                        "message": "OTP verified!",
                        "demo_mode": False
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid OTP!",
                        "demo_mode": False
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Service unavailable: {str(e)}",
                "demo_mode": False
            }


otp_service = OTPService()