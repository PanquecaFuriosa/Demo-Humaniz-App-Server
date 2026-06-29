from fastapi import APIRouter, Query, HTTPException, Response
from app.config import settings

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: int = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    # Loguea esto en la consola de Render para estar 100% seguros de qué está llegando
    print(f"DEBUG: Modo={hub_mode}, TokenRecibido={hub_verify_token}, Challenge={hub_challenge}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFICATION_TOKEN:
        # Retornar el número puro como string simple
        return Response(content=str(hub_challenge), media_type="text/plain", status_code=200)
    
    # Si llega aquí, es que el token no coincide
    raise HTTPException(status_code=403, detail="Forbidden")