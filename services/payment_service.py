import httpx
from config import settings


class PaymentService:

    async def charge_user(self, phone: str, reference_no: str = None) -> dict:
        """
        Demo mode: always success
        Production: bdApps directDebit
        """
        if settings.DEMO_MODE:
            return await self._demo_charge(phone)
        else:
            return await self._bdapps_charge(phone, reference_no)


    # ── Demo Mode ─────────────────────────────────────
    async def _demo_charge(self, phone: str) -> dict:
        print(f"[DEMO] Charged {settings.CHARGE_AMOUNT} BDT from {phone}")
        return {
            "success": True,
            "message": f"{settings.CHARGE_AMOUNT} BDT charged successfully!",
            "transaction_id": f"DEMO_TXN_{phone[-4:]}",
            "amount": settings.CHARGE_AMOUNT,
            "demo_mode": True
        }


    # ── Production Mode (bdApps) ──────────────────────
    async def _bdapps_charge(self, phone: str, reference_no: str) -> dict:
        try:
            import uuid
            external_txn_id = str(uuid.uuid4()).replace("-", "")[:32]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.BDAPPS_BASE_URL}/caas/direct/debit",
                    json={
                        "applicationId": settings.BDAPPS_APP_ID,
                        "password": settings.BDAPPS_PASSWORD,
                        "externalTrxId": external_txn_id,
                        "subscriberId": f"tel:{phone}",
                        "paymentInstrumentName": "MobileAccount",
                        "amount": settings.CHARGE_AMOUNT,
                        "currency": settings.CURRENCY
                    },
                    timeout=10.0
                )
                data = response.json()

                if data.get("statusCode") == "S1000":
                    return {
                        "success": True,
                        "message": f"{settings.CHARGE_AMOUNT} BDT charged!",
                        "transaction_id": data.get("internalTrxId"),
                        "reference_id": data.get("referenceId"),
                        "amount": settings.CHARGE_AMOUNT,
                        "demo_mode": False
                    }
                else:
                    return {
                        "success": False,
                        "message": "Payment failed! Insufficient balance?",
                        "demo_mode": False
                    }

        except Exception as e:
            return {
                "success": False,
                "message": f"Payment service unavailable: {str(e)}",
                "demo_mode": False
            }


    async def check_balance(self, phone: str) -> dict:
        """Check user's Robi/Airtel balance"""
        if settings.DEMO_MODE:
            return {
                "success": True,
                "balance": "100.0",
                "account_type": "Pre Paid",
                "account_status": "Active",
                "demo_mode": True
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.BDAPPS_BASE_URL}/caas/get/balance",
                    json={
                        "applicationId": settings.BDAPPS_APP_ID,
                        "password": settings.BDAPPS_PASSWORD,
                        "subscriberId": phone,
                        "paymentInstrumentName": "MobileAccount",
                        "currency": settings.CURRENCY
                    },
                    timeout=10.0
                )
                data = response.json()

                if data.get("statusCode") == "S1000":
                    return {
                        "success": True,
                        "balance": data.get("chargeableBalance"),
                        "account_type": data.get("accountType"),
                        "account_status": data.get("accountStatus"),
                        "demo_mode": False
                    }
                else:
                    return {
                        "success": False,
                        "message": "Could not fetch balance!",
                        "demo_mode": False
                    }

        except Exception as e:
            return {
                "success": False,
                "message": f"Service unavailable: {str(e)}",
                "demo_mode": False
            }


payment_service = PaymentService()