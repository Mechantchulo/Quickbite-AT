# Quickbite/app/api/v1/endpoints/ussd.py
import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ussd_session_event import UssdSessionEvent
from app.schemas.ussd import UssdEndEvent
from app.services.ussd_service import UssdPayload, UssdService

router = APIRouter(prefix="/ussd", tags=["USSD"])
logger = logging.getLogger(__name__)


async def _handle_ussd_core(request: Request, db: Session) -> PlainTextResponse:
    try:
        form = await request.form()
        ussd_service = UssdService(db)

        payload = UssdPayload(
            session_id=form.get("sessionId"),
            service_code=form.get("serviceCode"),
            phone_number=form.get("phoneNumber"),
            network_code=form.get("networkCode"),
            text=form.get("text", ""),
        )

        response_text = await ussd_service.handle(payload)
        # Guarantee AT-compatible prefix even if service accidentally returns malformed text.
        if not (response_text.startswith("CON ") or response_text.startswith("END ")):
            response_text = "END Service unavailable. Try again."
        return PlainTextResponse(response_text, media_type="text/plain")
    except Exception:
        logger.exception("USSD request processing failed")
        return PlainTextResponse("END Service unavailable. Try again.", media_type="text/plain")


@router.post("", response_class=PlainTextResponse)
async def handle_ussd(
    request: Request, db: Session = Depends(get_db)
) -> PlainTextResponse:
    return await _handle_ussd_core(request, db)


@router.post("/", response_class=PlainTextResponse)
async def handle_ussd_with_slash(
    request: Request, db: Session = Depends(get_db)
) -> PlainTextResponse:
    return await _handle_ussd_core(request, db)


@router.post("/events", status_code=status.HTTP_200_OK)
async def handle_ussd_end_event(
    request: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    form = await request.form()
    try:
        event = UssdEndEvent.model_validate(dict(form))
        db_event = UssdSessionEvent(
            session_id=event.session_id,
            service_code=event.service_code,
            network_code=event.network_code,
            phone_number=event.phone_number,
            date_utc=event.date,
            status=event.status,
            cost=event.cost,
            duration_in_millis=event.duration_in_millis,
            hops_count=event.hops_count,
            input=event.input,
            last_app_response=event.last_app_response,
            error_message=event.error_message,
        )
        db.add(db_event)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={"ok": True, "sessionId": event.session_id, "status": event.status},
        )
    except Exception:
        db.rollback()
        logger.exception("Failed to persist USSD end-session event")
        return JSONResponse(status_code=200, content={"ok": False, "message": "ignored"})
