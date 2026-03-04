from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class UssdSessionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    session_id: str = Field(alias="sessionId")
    service_code: str = Field(alias="serviceCode")
    phone_number: str = Field(alias="phoneNumber")
    network_code: str = Field(alias="networkCode")
    text: str = ""


class UssdEndEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    date: str
    session_id: str = Field(alias="sessionId")
    service_code: str = Field(alias="serviceCode")
    network_code: str = Field(alias="networkCode")
    phone_number: str = Field(alias="phoneNumber")
    status: Literal["Success", "Incomplete", "Failed"]
    cost: str
    duration_in_millis: str = Field(alias="durationInMillis")
    hops_count: int = Field(alias="hopsCount")
    input: str
    last_app_response: str = Field(alias="lastAppResponse")
    error_message: str | None = Field(default=None, alias="errorMessage")
