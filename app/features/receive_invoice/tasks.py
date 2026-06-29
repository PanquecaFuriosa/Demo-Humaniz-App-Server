from app.features.receive_invoice.service import invoice_service

async def process_invoice_async(image_id: str, sender: str):
    print(f"[Task] Hilo asíncrono iniciado para la imagen {image_id}")
    try:
        # The task only invokes the service use case.
        await invoice_service.execute_processing(image_id, sender)
    except Exception as e:
        print(f"[Task] Error crítico en el hilo de segundo plano: {e}")