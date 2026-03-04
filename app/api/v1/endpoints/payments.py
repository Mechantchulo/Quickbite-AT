# Quickbite/app/api/v1/endpoints/payments.py
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.models.order import Order, OrderStatus
from app.services.payment_service import send_stk_push

router = APIRouter(prefix="/payments", tags=["Payments"])


def require_internal_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = settings.INTERNAL_API_KEY
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def verify_payhero_callback_token(
    x_callback_token: str | None = Header(default=None),
) -> None:
    expected = settings.PAYHERO_CALLBACK_TOKEN
    if expected and x_callback_token != expected:
        raise HTTPException(status_code=401, detail="Invalid callback token")


class StkPushRequest(BaseModel):
    amount: int = Field(..., gt=0)
    phone_number: str = Field(..., min_length=10)
    external_reference: str = Field(..., min_length=1)
    customer_name: str = Field(..., min_length=1)


class StkPushResponse(BaseModel):
    success: bool
    data: dict[str, Any]


@router.post("/stk-push", response_model=StkPushResponse)
async def create_stk_push(
    payload: StkPushRequest, _: None = Depends(require_internal_api_key)
) -> dict:
    try:
        response = send_stk_push(
            amount=payload.amount,
            phone_number=payload.phone_number,
            external_reference=payload.external_reference,
            customer_name=payload.customer_name,
        )
        return {"success": True, "data": response}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"STK push failed: {exc}") from exc


@router.post("/callback")
async def payhero_callback(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(verify_payhero_callback_token),
) -> dict:
    # PayHero usually posts JSON; this fallback also supports form data.
    try:
        body = await request.json()
    except Exception:
        form = await request.form()
        body = dict(form)

    # Flexible extraction (adjust keys to your exact PayHero payload)
    provider_ref = (
        body.get("provider_ref")
        or body.get("CheckoutRequestID")
        or body.get("checkout_request_id")
        or body.get("reference")
    )
    external_reference = (
        body.get("external_reference")
        or body.get("ExternalReference")
        or body.get("merchant_reference")
    )
    status_raw = str(
        body.get("status")
        or body.get("ResultCode")
        or body.get("result_code")
        or ""
    ).strip().lower()

    # Decide final status
    success_values = {"success", "completed", "paid", "0"}
    new_status = OrderStatus.PAID if status_raw in success_values else OrderStatus.FAILED

    stmt = None
    if provider_ref:
        stmt = select(Order).where(Order.provider_ref == provider_ref)
    elif external_reference:
        # external_reference is set to order.id in STK push, fallback to session_id too
        stmt = select(Order).where(Order.session_id == external_reference)
        try:
            order_id = UUID(str(external_reference))
            stmt = select(Order).where(
                or_(Order.id == order_id, Order.session_id == external_reference)
            )
        except ValueError:
            pass

    if stmt is None:
        return {"ok": False, "message": "No reference provided"}

    order = db.execute(stmt).scalar_one_or_none()
    if not order:
        return {"ok": False, "message": "Order not found"}

    # Idempotent update
    if order.status in {OrderStatus.PAID, OrderStatus.FAILED}:
        return {"ok": True, "message": "Already finalized", "order_status": order.status.value}

    order.status = new_status
    if provider_ref and not order.provider_ref:
        order.provider_ref = provider_ref

    db.add(order)
    db.commit()

    return {"ok": True, "order_id": str(order.id), "order_status": order.status.value}
