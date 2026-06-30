import requests

def process_invoice_async(message_content: dict, sender: str, message_id: str):
    # 'message_content' contains the {"imageMessage": {...}} dictionary forwarded by the router
    
    url_evolution = "https://demo-humaniz-evolution-api-gateway.onrender.com/chat/getBase64FromMediaMessage/my_first_test"
    headers = {
        "apikey": "MySecureInvoiceToken2026",
        "Content-Type": "application/json"
    }
    payload = {
        "message": message_content
    }
    
    response = requests.post(url_evolution, json=payload, headers=headers)
    if response.status_code == 200:
        # This returns the decrypted file as a Base64 string, ready for your OCR / AI logic
        base64_data = response.json().get("base64") 
        
        print(f"[Task] Successfully downloaded image buffer from message {message_id}")
        # ... Execute your business logic here (Supabase storage, AI parser, etc.)
    else:
        print(f"[Task] Failed to download media from Evolution API: {response.text}")