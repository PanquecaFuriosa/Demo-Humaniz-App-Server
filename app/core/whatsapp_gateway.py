import os
import base64
import httpx
from app.config import settings

class WhatsAppGateway:
    def __init__(self) -> None:
        # These should ideally come from your app.config.settings
        self.url_evolution = "https://demo-humaniz-evolution-api-gateway.onrender.com/chat/getBase64FromMediaMessage/my_first_test"
        self.api_key = "MySecureInvoiceToken2026"

    async def download_image(self, message_content: dict, message_id: str, sender: str) -> str | None:
        """
        SRP: Solely responsible for interacting with the Evolution API 
        and storing the temporary physical asset.
        """
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        payload = { "message": message_content }
        
        try:
            # Leverage httpx for non-blocking asynchronous HTTP requests
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.url_evolution, json=payload, headers=headers)
            
            if not response.is_success:
                print(f"[WhatsApp Gateway] Remote API returned status code: {response.status_code}")
                return None

            base64_data = response.json().get("base64")
            if not base64_data:
                print("[WhatsApp Gateway] Base64 payload missing in response.")
                return None
                
            print(f"[WhatsApp Gateway] Successfully fetched media buffer for message: {message_id}")
            
            # Decode binary payload and commit to ephemeral disk storage
            image_bytes = base64.b64decode(base64_data)
            filename = f"factura_{message_id}.jpg"
            
            with open(filename, "wb") as file:
                file.write(image_bytes)
                
            print(f"[WhatsApp Gateway] Temporary asset persisted at: {filename}")
            return filename
            
        except Exception as e:
            print(f"[WhatsApp Gateway] Exception caught during media download: {e}")
            return None

    async def send_message(self, remote_jid: str, text: str) -> bool:
        """Dispatches outbound text notifications back to the user via Evolution API."""
        # TODO: Implement your outbound WhatsApp message HTTP call here
        print(f"[WhatsApp Gateway] Simulating outbound text to {remote_jid}")
        return True

whatsapp_gateway = WhatsAppGateway()