from fastapi import APIRouter, BackgroundTasks, Request
from app.config import settings
from app.features.receive_invoice.service import invoice_service 

router = APIRouter()

@router.post("/webhook")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        
        # 1. Event verification guard clause
        if payload.get("event") != "messages.upsert":
            return {"status": "ignored_event"}
            
        message_data = payload.get("data", {})
        key = message_data.get("key", {})
        
        # 2. Strict identity verification: Ignore outbound responses from the system identity
        if key.get("fromMe") is True:
            return {"status": "ignored_self"}
            
        # 3. Normalize sender identification
        remote_jid = key.get("remoteJid", "")
        sender = remote_jid.split("@")[0] if remote_jid else ""
        
        # 4. Extract down-nested content
        message_content = message_data.get("message", {})

        # --- MULTIMODAL ROUTING PATHWAY ---
        if "imageMessage" in message_content:
            message_id = key.get("id") 
            
            print(f"[Router] Image payload detected from sender {sender}. Handoff to async service worker pool...")
            
            # Offload use-case orchestration to the service layer asynchronously
            background_tasks.add_task(
                invoice_service.execute_processing, 
                message_content, 
                message_id, 
                sender
            )
            
        # --- TEXT ROUTING PATHWAY ---
        elif "conversation" in message_content or "extendedTextMessage" in message_content:
            text_body = (
                message_content.get("conversation") or 
                message_content.get("extendedTextMessage", {}).get("text", "")
            )
            print(f"[Router] Inbound conversational stream text from {sender}: {text_body}")
            
    except Exception as e:
        print(f"[Router] Critical anomaly encountered during incoming payload processing: {e}")
        
    # Standard early response pattern to guarantee immediate release of the calling worker node
    return {"status": "accepted"}