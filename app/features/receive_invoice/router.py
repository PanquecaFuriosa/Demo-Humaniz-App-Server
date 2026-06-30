from fastapi import APIRouter, BackgroundTasks, Request
from app.features.receive_invoice.tasks import process_invoice_async
from app.config import settings

router = APIRouter()

@router.post("/webhook")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    try:
        # Fetch the JSON payload directly from the request
        payload = await request.json()
        
        # 1. Validate that it's a new message event
        if payload.get("event") != "messages.upsert":
            return {"status": "ignored_event"}
            
        message_data = payload.get("data", {})
        key = message_data.get("key", {})
        
        # 2. CRITICAL FILTER: Ignore if the message was sent by the bot itself
        if key.get("fromMe") is True:
            return {"status": "ignored_self"}
            
        # 3. Extract sender (Comes as "584129906876@s.whatsapp.net")
        remote_jid = key.get("remoteJid", "")
        sender = remote_jid.split("@")[0] if remote_jid else ""
        
        # 4. Extract message body content
        message_content = message_data.get("message", {})
        
        # --- CASE 1: IMAGE DETECTION ---
        if "imageMessage" in message_content:
            image_block = message_content["imageMessage"]
            
            # In Evolution API, you need the full message block to download the media later,
            # but you can use the key ID as a reference identifier.
            message_id = key.get("id") 
            
            print(f"[Router] Image detected from {sender}. Scheduling background task...")
            
            # Pass the structured data to your background worker
            background_tasks.add_task(process_invoice_async, message_content, sender, message_id)
            
        # --- CASE 2: TEXT DETECTION ---
        elif "conversation" in message_content or "extendedTextMessage" in message_content:
            text_body = (
                message_content.get("conversation") or 
                message_content.get("extendedTextMessage", {}).get("text", "")
            )
            print(f"[Router] Text received from {sender}: {text_body}")
            
    except Exception as e:
        print(f"[Router] Critical error parsing Evolution Webhook: {e}")
        
    # Always respond with a 200 OK immediately to free up the Evolution API worker
    return {"status": "accepted"}