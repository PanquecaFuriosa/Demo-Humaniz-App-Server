import httpx
import base64
import os
from app.config import settings 

class WhatsAppGateway:
    def __init__(self):
        self.base_url = "https://demo-humaniz-evolution-api-gateway.onrender.com"
        self.apikey = "MySecureInvoiceToken2026"
        self.instance_name = "my_first_test"

    async def download_image(self, message_content: dict, message_id: str, sender: str) -> str | None:
        """
        Consumes Evolution API decryption endpoint, decodes the Base64 response,
        and saves it to the local disk for Gemini to ingest.
        """
        url = f"{self.base_url}/chat/getBase64FromMediaMessage/{self.instance_name}"
        headers = {
            "apikey": self.apikey,
            "Content-Type": "application/json"
        }
        payload = {
            "message": message_content
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                
            if response.status_code == 200:
                base64_data = response.json().get("base64")
                if not base64_data:
                    print("[WhatsAppGateway] No base64 data found in API response.")
                    return None

                # 1. Decodes the Base64 bytes
                image_bytes = base64.b64decode(base64_data)

                # 2. Ensures that the destination directory exists locally.
                output_dir = "data/invoices"
                os.makedirs(output_dir, exist_ok=True)
                
                # 3. Saves the file to disk
                saved_path = f"{output_dir}/{message_id}.jpg"
                with open(saved_path, "wb") as f:
                    f.write(image_bytes)

                print(f"[WhatsAppGateway] Imagen guardada exitosamente en: {saved_path}")
                return saved_path
            else:
                print(f"[WhatsAppGateway] Error de la API al desencriptar: {response.text}")
                return None

        except Exception as e:
            print(f"[WhatsAppGateway] Error en la descarga/escritura de medios: {e}")
            return None

    async def send_message(self, sender: str, text: str) -> bool:
        """Sends an outbound text message using Evolution API format"""
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        headers = {
            "apikey": self.apikey,
            "Content-Type": "application/json"
        }
        
        # Note: Evolution API prefers receiving the number with or without @s.whatsapp.net,
        # but to ensure compatibility, we send the cleaned number string.
        payload = {
            "number": sender,
            "text": text
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"[WhatsAppGateway] Error enviando mensaje a {sender}: {e}")
            return False

whatsapp_gateway = WhatsAppGateway()