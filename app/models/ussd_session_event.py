from datetime import datetime
import uuid

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class UssdSessionEvent(Base):
    __tablename__ = "ussd_session_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    session_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    service_code: Mapped[str] = mapped_column(String(30), nullable=False)
    network_code: Mapped[str] = mapped_column(String(10), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)

    date_utc: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False)

    cost: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_in_millis: Mapped[str] = mapped_column(String(20), nullable=False)
    hops_count: Mapped[int] = mapped_column(Integer, nullable=False)

    input: Mapped[str] = mapped_column(Text, nullable=False)
    last_app_response: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
