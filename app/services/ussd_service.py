
import asyncio
from dataclasses import dataclass

from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.order import ItemCode, Order, OrderStatus
from app.services.payment_service import send_stk_push

@dataclass
class UssdPayload:
    session_id: str | None
    service_code: str | None
    phone_number: str | None
    network_code: str | None
    text: str


class UssdService:
    def __init__(self, db: Session):
        self.db = db

    MENU = {
        "1": ("BURGER", 20),
        "2": ("CHIPS", 50),
        "3": ("SODA", 30),
    }

    @staticmethod
    def _parse_positive_int(value: str) -> int | None:
        try:
            n = int(value)
            return n if n > 0 else None
        except (TypeError, ValueError):
            return None

    async def handle(self, payload: UssdPayload) -> str:
        text = (payload.text or "").strip()
        parts = text.split("*") if text else []

        if text == "":
            return (
                "CON QuickBite\n"
                "1. Burger - 20\n"
                "2. Chips - 50\n"
                "3. Soda - 30\n"
                "4. My last order\n"
                "0. Exit"
            )

        if parts[0] == "0":
            return "END Goodbye."

        if parts[0] == "4":
            if not payload.phone_number:
                return "END Phone number is missing."

            stmt = (
                select(Order)
                .where(Order.phone == payload.phone_number)
                .order_by(desc(Order.created_at))
                .limit(1)
            )
            last_order = self.db.execute(stmt).scalar_one_or_none()

            if not last_order:
                return "END No previous order found."

            return (
                "END Last order\n"
                f"Item: {last_order.item_code.value}\n"
                f"Qty: {last_order.qty}\n"
                f"Total: KES {last_order.amount}\n"
                f"Status: {last_order.status.value}"
            )

        if parts[0] not in self.MENU:
            return "END Invalid choice."

        item_code, unit_price = self.MENU[parts[0]]

        if len(parts) == 1:
            return "CON Enter quantity:"

        qty = self._parse_positive_int(parts[1])
        if qty is None:
            return "END Invalid quantity."

        total = qty * unit_price

        if len(parts) == 2:
            return (
                "CON Confirm order\n"
                f"Item: {item_code}\n"
                f"Qty: {qty}\n"
                f"Total: KES {total}\n"
                "1. Confirm\n"
                "2. Cancel"
            )

        if len(parts) == 3:
            if parts[2] == "1":
                if not payload.session_id or not payload.phone_number:
                    return "END Missing session or phone details."

                order = Order(
                    session_id=payload.session_id,
                    phone=payload.phone_number,
                    item_code=ItemCode[item_code],
                    qty=qty,
                    amount=total,
                )

                try:
                    self.db.add(order)
                    self.db.flush()

                    stk_response = await asyncio.to_thread(
                        send_stk_push,
                        amount=total,
                        phone_number=payload.phone_number,
                        external_reference=str(order.id),
                        customer_name="QuickBite Customer",
                    )

                    provider_ref = stk_response.get("provider_ref")
                    if provider_ref:
                        order.provider_ref = str(provider_ref)
                    order.status = OrderStatus.STK_SENT

                    self.db.commit()
                except SQLAlchemyError:
                    self.db.rollback()
                    return "END We could not place your order. Try again."
                except Exception:
                    self.db.rollback()
                    return "END Payment request failed. Try again."

                return "END Payment prompt sent. Enter M-Pesa PIN."
            if parts[2] == "2":
                return "END Order cancelled."
            return "END Invalid choice."

        return "END Invalid input."
