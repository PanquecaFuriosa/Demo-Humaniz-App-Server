from fastapi import APIRouter, Query, Response, HTTPException
from app.config import settings

router = APIRouter()

@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: int = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFICATION_TOKEN:
        return Response(content=str(hub_challenge), media_type="text/plain")
    raise HTTPException(status_code=403, detail="Token de verificación inválido")