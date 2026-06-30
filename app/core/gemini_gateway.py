import os
import mimetypes
from google import genai
from google.genai import types
from app.config import settings
from app.features.receive_invoice.schemas import MobilePaymentData

class GeminiGateway:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Targeted multimodal model optimized for structural extraction
        self.model_name = "gemini-3.5-flash"

    async def analyze_mobile_payment(self, image_path: str) -> MobilePaymentData | None:
        """
        Loads the local image into a memory buffer and dispatches it asynchronously 
        to Gemini, returning highly precise structured Pydantic data.
        """
        if not os.path.exists(image_path):
            print(f"[Gemini Gateway] Error: Target file context missing at {image_path}")
            return None

        try:
            # Determine the exact MIME type dynamically (e.g., image/jpeg, image/png)
            mime_type, _ = mimetypes.guess_type(image_path)
            mime_type = mime_type or "image/jpeg"

            # Read file bytes instantly and close the file descriptor immediately.
            # This ensures the OS releases the file lock before the long network await.
            with open(image_path, "rb") as file:
                image_bytes = file.read()

            # Wrap the raw buffer into the official GenAI content Part format
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
            
            prompt = (
                "Analiza detalladamente esta captura de pantalla de un Pago Móvil bancario. "
                "Extrae los datos solicitados de forma precisa. Si no logras visualizar un campo con certeza, "
                "coloca 'No detectado'."
            )

            print("[Gemini Gateway] Dispatching payload to Gemini for structured vision analysis...")
            
            # Non-blocking remote I/O call via the asynchronous client bundle
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MobilePaymentData,
                    temperature=0.1  # Guardrails to maximize factual data alignment
                ),
            )
            
            # Directly validate and serialize the structured response payload
            structured_data = MobilePaymentData.model_validate_json(response.text)
            return structured_data

        except Exception as e:
            print(f"[Gemini Gateway] Critical runtime failure during AI processing pipeline: {e}")
            return None

gemini_gateway = GeminiGateway()