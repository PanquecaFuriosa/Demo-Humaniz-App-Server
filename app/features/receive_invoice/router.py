from fastapi import APIRouter, BackgroundTasks
from app.features.receive_invoice.tasks import process_invoice_async
from app.config import settings

router = APIRouter()

@router.post("/webhook")
async def receive_whatsapp_message(data: dict, background_tasks: BackgroundTasks):
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            mensaje = value["messages"][0]
            message_type = mensaje.get("type")
            sender = mensaje.get("from")
            
            if message_type == "image":
                image_id = mensaje["image"]["id"]
                print(f"[Router] Imagen detectada. Agendando tarea en segundo plano...")
                
                # Handles the asynchronous task natively in FastAPI
                background_tasks.add_task(process_invoice_async, image_id, sender)
                
            elif message_type == "text":
                print(f"[Router] Texto recibido de {sender}: {mensaje['text']['body']}")
                
    except Exception as e:
        print(f"[Router] Error parseando Webhook: {e}")
        
    # Always responds to Meta with a "200 OK" quickly to free up the connection.
    return {"status": "accepted"}