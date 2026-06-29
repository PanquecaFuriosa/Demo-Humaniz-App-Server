# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.features.webhook_verification.router import router as verification_router
from app.features.receive_invoice.router import router as receive_invoice_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the tables if they do not exist when the server starts
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Humaniz Invoice Automation API", version="1.0.0", lifespan=lifespan)

app.include_router(verification_router)
app.include_router(receive_invoice_router)