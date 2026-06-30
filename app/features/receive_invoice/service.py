from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.core.whatsapp_gateway import whatsapp_gateway
from app.core.gemini_gateway import gemini_gateway
from app.features.receive_invoice.models import InvoiceAudit
from app.features.receive_invoice.schemas import MobilePaymentData

class ReceiveInvoiceService:
    async def execute_processing(self, message_content: dict, message_id: str, sender: str) -> None:
        """Coordinates the use case and persists the states in the database"""
        
        # 1. Create the initial audit record (Status: RECEIVED) using message_id
        async with AsyncSessionLocal() as db:
            audit_record = InvoiceAudit(whatsapp_id=message_id, sender=sender, status="RECEIVED")
            db.add(audit_record)
            await db.commit()
            await db.refresh(audit_record)

            try:
                # 2. Update to PROCESSING status
                audit_record.status = "PROCESSING"
                await db.commit()

                # 3. Download image 
                # CAMBIO: Pasamos el bloque del mensaje para desencriptación
                saved_path = await whatsapp_gateway.download_image(message_content, message_id, sender)
                if not saved_path:
                    audit_record.status = "FAILED"
                    audit_record.error_log = "Error downloading the image from Evolution API."
                    await db.commit()
                    await whatsapp_gateway.send_message(sender, "No pudimos descargar tu imagen.")
                    return

                audit_record.local_path = saved_path
                await db.commit()

                # 4. Process with AI -> ¡ESTO QUEDA EXACTAMENTE IGUAL!
                payment_data = await gemini_gateway.analyze_mobile_payment(saved_path)
                if not payment_data:
                    audit_record.status = "FAILED"
                    audit_record.error_log = "Gemini failed to extract valid structured data."
                    await db.commit()
                    await whatsapp_gateway.send_message(sender, "No logramos extraer los datos automáticamente.")
                    return

                # 5. Save the successfully extracted data (Status: COMPLETED) -> IGUAL
                audit_record.issuing_bank = payment_data.issuing_bank
                audit_record.reference = payment_data.reference
                audit_record.amount = payment_data.amount
                audit_record.status = "COMPLETED"
                await db.commit()

                # 6. Notify the user via WhatsApp
                message = self._construct_success_message(payment_data)
                await whatsapp_gateway.send_message(sender, message)

            except Exception as e:
                await db.rollback()
                audit_record.status = "FAILED"
                audit_record.error_log = str(e)
                await db.commit()
                print(f"[Service] Error crítico registrado en auditoría: {e}")

    def _construct_success_message(self, data: MobilePaymentData) -> str:
        return (
            "*¡Pago Móvil Recibido y Registrado!*\n\n"
            f"Banco: {data.issuing_bank}\n"
            f"Referencia: {data.reference}\n"
            f"Monto: {data.amount} Bs.\n"
            f"Fecha: {data.date}\n\n"
            "_Su transacción ha sido auditada y guardada en base de datos._"
        )

invoice_service = ReceiveInvoiceService()