# Quickbite/app/main.py
from fastapi import FastAPI
from app.api.v1.endpoints.ussd import router as ussd_router
from app.api.v1.endpoints.payments import router as payments_router



app = FastAPI(title="QuickBite USSD")
app.include_router(ussd_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")