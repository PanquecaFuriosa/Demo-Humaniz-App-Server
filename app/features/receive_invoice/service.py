import os
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.core.whatsapp_gateway import whatsapp_gateway
from app.core.gemini_gateway import gemini_gateway
from app.features.receive_invoice.models import InvoiceAudit
from app.features.receive_invoice.schemas import MobilePaymentData

class ReceiveInvoiceService:
    async def execute_processing(self, message_content: dict, message_id: str, sender: str) -> None:
        """
        Coordinates the core business use case.
        Maintains granular database context boundaries to safeguard the connection pool.
        """
        # Step 1: Initialize audit footprint
        async with AsyncSessionLocal() as db:
            audit_record = InvoiceAudit(whatsapp_id=message_id, sender=sender, status="RECEIVED")
            db.add(audit_record)
            await db.commit()
            
        saved_path = None

        try:
            # Step 2: Elevate state to PROCESSING
            await self._update_audit_status(message_id, "PROCESSING")

            # Step 3: Offload asset retrieval to the Infrastructure Layer
            saved_path = await whatsapp_gateway.download_image(message_content, message_id, sender)
            if not saved_path:
                await self._handle_failure(
                    whatsapp_id=message_id, 
                    sender=sender, 
                    error_log="Evolution API media retrieval failure.", 
                    user_message="No pudimos descargar tu imagen."
                )
                return

            # Bind local path metadata to the current audit scope
            await self._update_local_path(message_id, saved_path)

            # Step 4: Outsource Vision/AI analysis to the Gemini Gateway
            payment_data = await gemini_gateway.analyze_mobile_payment(saved_path)
            if not payment_data:
                await self._handle_failure(
                    whatsapp_id=message_id, 
                    sender=sender, 
                    error_log="Gemini vision model extraction yielded null/empty structured data.", 
                    user_message="No logramos extraer los datos automáticamente."
                )
                return

            # Step 5: Finalize transaction tracking state to COMPLETED
            await self._finalize_audit_success(message_id, payment_data)

            # Step 6: Trigger consumer notification
            success_message = self._construct_success_message(payment_data)
            await whatsapp_gateway.send_message(sender, success_message)

        except Exception as e:
            print(f"[Service] Critical runtime exception caught within message execution {message_id}: {e}")
            await self._handle_failure(message_id, sender, f"Unexpected execution crash: {str(e)}")

        finally:
            # Step 7: Strict IO Clean-up boundary condition
            if saved_path and os.path.exists(saved_path):
                try:
                    os.remove(saved_path)
                    print(f"[Service] Ephemeral storage cleared. Deleted: {saved_path}")
                except Exception as cleanup_error:
                    print(f"[Service] Failed to purge resource at {saved_path}: {cleanup_error}")

    # --- ISOLATED REUSABLE DATABASE MUTATIONS ---

    async def _update_audit_status(self, whatsapp_id: str, status: str) -> None:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(InvoiceAudit).where(InvoiceAudit.whatsapp_id == whatsapp_id))
            record = result.scalar_one_or_none()
            if record:
                record.status = status
                await db.commit()

    async def _update_local_path(self, whatsapp_id: str, path: str) -> None:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(InvoiceAudit).where(InvoiceAudit.whatsapp_id == whatsapp_id))
            record = result.scalar_one_or_none()
            if record:
                record.local_path = path
                await db.commit()

    async def _finalize_audit_success(self, whatsapp_id: str, data: MobilePaymentData) -> None:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(InvoiceAudit).where(InvoiceAudit.whatsapp_id == whatsapp_id))
            record = result.scalar_one_or_none()
            if record:
                record.issuing_bank = data.issuing_bank
                record.reference = data.reference
                record.amount = data.amount
                record.status = "COMPLETED"
                await db.commit()

    async def _handle_failure(self, whatsapp_id: str, sender: str, error_log: str, user_message: str = None) -> None:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(InvoiceAudit).where(InvoiceAudit.whatsapp_id == whatsapp_id))
            record = result.scalar_one_or_none()
            if record:
                record.status = "FAILED"
                record.error_log = error_log
                await db.commit()
        
        if user_message:
            await whatsapp_gateway.send_message(sender, user_message)

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