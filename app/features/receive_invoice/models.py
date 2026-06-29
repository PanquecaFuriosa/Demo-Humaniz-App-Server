from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.core.database import Base

class InvoiceAudit(Base):
    __tablename__ = "invoice_audits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    whatsapp_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    sender: Mapped[str] = mapped_column(String(50), nullable=False)
    local_path: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Fields extracted by AI (may be null initially while processing)
    issuing_bank: Mapped[str] = mapped_column(String(100), nullable=True)
    reference: Mapped[str] = mapped_column(String(100), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    
    # State Control (Lifecycle)
    status: Mapped[str] = mapped_column(String(30), default="RECEIVED")  # RECEIVED, PROCESSING, COMPLETED, FAILED
    error_log: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )