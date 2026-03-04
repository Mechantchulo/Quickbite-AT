import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.order import ItemCode, OrderStatus


class OrderCreate(BaseModel):
    session_id: str
    phone: str
    item_code: ItemCode
    qty: int = Field(ge=1)
    amount: int = Field(gt=0)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: str
    phone: str
    item_code: ItemCode
    qty: int
    amount: int
    status: OrderStatus
    provider_ref: str | None = None
    created_at: datetime
    updated_at: datetime
