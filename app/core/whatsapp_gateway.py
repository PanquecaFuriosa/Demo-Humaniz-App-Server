import os
import httpx
from app.config import settings

class WhatsAppGateway:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        os.makedirs(settings.DOWNLOADS_DIR, exist_ok=True)
        self.send_url = f"https://graph.facebook.com/v25.0/{settings.PHONE_NUMBER_ID}/messages"

    async def download_image(self, image_id: str, sender: str) -> str | None:
        """Two-step workflow to download file bytes from Meta"""
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Obtain the temporary URL
                url_api = f"https://graph.facebook.com/v25.0/{image_id}"
                response = await client.get(url_api, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"[Gateway] Error obteniendo metadatos: {response.text}")
                    return None
                    
                real_download_url = response.json().get("url")
                if not real_download_url:
                    return None
                    
                # Step 2: Download the binary
                print("[Gateway] Descargando bytes de la imagen...")
                response_file = await client.get(real_download_url, headers=self.headers)
                
                if response_file.status_code == 200:
                    file_path = f"{settings.DOWNLOADS_DIR}/factura_{sender}_{image_id}.jpg"
                    with open(file_path, "wb") as f:
                        f.write(response_file.content)
                    return file_path
                    
            except Exception as e:
                print(f"[Gateway] Error crítico en descarga: {e}")
        return None
    
    async def send_message(self, receiver: str, texto: str) -> bool:
        """Send a free text message to a WhatsApp number via Meta"""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": receiver,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": texto
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"[Gateway] Enviando respuesta a WhatsApp para {receiver}...")
                response = await client.post(self.send_url, headers=self.headers, json=payload)
                
                if response.status_code in [200, 201]:
                    print(f"[Gateway] Mensaje enviado con éxito a {receiver}.")
                    return True
                else:
                    print(f"[Gateway] Error al enviar mensaje: {response.status_code} - {response.text}")
                    return False
            except Exception as e:
                print(f"[Gateway] Error crítico enviando mensaje: {e}")
                return False

whatsapp_gateway = WhatsAppGateway()