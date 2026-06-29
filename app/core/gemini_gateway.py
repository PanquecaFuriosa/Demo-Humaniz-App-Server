import os
from google import genai
from google.genai import types
from PIL import Image
from app.config import settings
from app.features.receive_invoice.schemas import MobilePaymentData

class GeminiGateway:
    def __init__(self):
        # Initialize the official client using the API Key from the config
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # We use the Flash model, which is ultra-fast and excellent for structured multimodal processing.
        self.model_name = "gemini-3.5-flash"

    async def analyze_mobile_payment(self, image_path: str) -> MobilePaymentData | None:
        """Opens a local image, sends it to Gemini, and returns the structured data"""
        if not os.path.exists(image_path):
            print(f"[Gemini Gateway] Error: El archivo {image_path} no existe.")
            return None

        try:
            # Opens the image using PIL (Pillow) to pass the bytes to the SDK.
            img = Image.open(image_path)
            
            prompt = (
                "Analiza detalladamente esta captura de pantalla de un Pago Móvil bancario. "
                "Extrae los datos solicitados de forma precisa. Si no logras visualizar un campo con certeza, "
                "coloca 'No detectado'."
            )

            print("[Gemini Gateway] Enviando imagen a Gemini para análisis estructurado...")
            
            # Calls the API, forcing a structured response (Structured Outputs).
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[img, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MobilePaymentData,
                    temperature=0.1 # Low temperature to ensure it is deterministic and precise.
                ),
            )
            
            # The SDK automatically validates and parses the JSON string back into our Pydantic object.
            structured_data = MobilePaymentData.model_validate_json(response.text)
            return structured_data

        except Exception as e:
            print(f"[Gemini Gateway] Error crítico procesando la imagen con IA: {e}")
            return None

gemini_gateway = GeminiGateway()