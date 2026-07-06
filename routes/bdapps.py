from fastapi import APIRouter, Request
import json

router = APIRouter()


@router.get("/api/bdapps/connect")
async def bdapps_connect(request: Request):
    """bdApps connection verification"""
    return {"status": "OK", "message": "PromptForge Academy connected"}


@router.post("/api/bdapps/notify")
async def bdapps_notify(request: Request):
    """bdApps notification callback"""
    try:
        body = await request.json()
        print(f"[bdApps Notify] {json.dumps(body)}")
    except:
        pass
    return {"status": "OK"}


@router.post("/api/bdapps/subscribe")
async def bdapps_subscribe(request: Request):
    """bdApps subscription callback"""
    try:
        body = await request.json()
        print(f"[bdApps Subscribe] {json.dumps(body)}")
    except:
        pass
    return {"status": "OK"}