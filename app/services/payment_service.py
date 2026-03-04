
from typing import Any

import requests

from app.core.config import settings


def _build_headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    auth = settings.PAYHERO_BASIC_AUTH.strip()
    if auth:
        headers["Authorization"] = auth
    return headers


def _normalize_phone(phone_number: str) -> str:
    p = phone_number.strip().replace("+", "")
    if p.startswith("0") and len(p) == 10:
        return f"254{p[1:]}"
    if p.startswith("254") and len(p) == 12:
        return p
    raise ValueError("phone_number must be 07XXXXXXXX or 2547XXXXXXXX")


def send_stk_push(
    amount: int,
    phone_number: str,
    external_reference: str,
    customer_name: str,
) -> dict[str, Any]:
    url = settings.URL
    callback_url = settings.CALLBACK_URL
    provider = settings.PROVIDER.strip().lower()
    channel_id = settings.CHANNEL_ID

    if not url:
        raise ValueError("Missing URL in environment")
    if not callback_url:
        raise ValueError("Missing CALLBACK_URL in environment")
    if channel_id is None:
        raise ValueError("Missing CHANNEL_ID in environment")

    payload = {
        "amount": int(amount),
        "phone_number": _normalize_phone(phone_number),
        "external_reference": external_reference,
        "customer_name": customer_name,
        "channel_id": int(channel_id),
        "provider": provider,
        "callback_url": callback_url,
    }

    response = requests.post(
        url,
        json=payload,
        headers=_build_headers(),
        timeout=30,
    )
    if not response.ok:
        raise ValueError(f"PayHero {response.status_code}: {response.text}")

    try:
        data = response.json()
    except ValueError:
        return {"status_code": response.status_code, "response": response.text}

    provider_ref = (
        data.get("provider_ref")
        or data.get("CheckoutRequestID")
        or data.get("checkout_request_id")
        or data.get("reference")
    )

    return {
        "raw": data,
        "provider_ref": provider_ref,
        "external_reference": external_reference,
    }
