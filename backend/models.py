"""Pydantic v2 data contracts for freight loads and call-log webhook payloads."""

from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field


class LoadModel(BaseModel):
    """Freight load record mapped to the ``loads`` table schema."""

    load_id: str = Field(..., description="Primary key. Unique load identifier.")
    origin: str = Field(..., description="Pickup location city/state.")
    destination: str = Field(..., description="Delivery location city/state.")
    pickup_datetime: AwareDatetime = Field(
        ...,
        description="Timezone-aware pickup date and time (ISO 8601).",
    )
    delivery_datetime: AwareDatetime = Field(
        ...,
        description="Timezone-aware delivery date and time (ISO 8601).",
    )
    equipment_type: str = Field(
        ...,
        description="Required equipment type (e.g., Reefer, Dry Van).",
    )
    loadboard_rate: float = Field(
        ...,
        gt=0,
        description="Listed baseline rate for the load.",
    )
    weight: float = Field(..., description="Load weight in pounds.")
    commodity_type: str = Field(..., description="Type of goods being transported.")
    num_of_pieces: int = Field(..., description="Number of physical items in the load.")
    miles: float = Field(..., description="Total distance to travel.")
    dimensions: str = Field(..., description="Size measurements for the freight.")
    notes: str | None = Field(
        default=None,
        description="Optional additional load information.",
    )


class CallLogModel(BaseModel):
    """Inbound HappyRobot webhook payload for post-call operational metrics."""

    call_id: str = Field(..., description="Primary key. Unique call identifier from HappyRobot.")
    carrier_mc: str = Field(..., description="Motor Carrier identifier evaluated during the call.")
    load_id: str = Field(..., description="Foreign key referencing ``loads.load_id``.")
    final_rate: float = Field(
        ...,
        gt=0,
        description="Agreed settlement price when the call outcome is BOOKED.",
    )
    outcome: Literal["BOOKED", "REJECTED_RATE", "VETTING_FAILED", "HUNG_UP"] = Field(
        ...,
        description="Structured call disposition status.",
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        ...,
        description="Carrier attitude classification from the conversation.",
    )
    duration_seconds: int = Field(
        ...,
        ge=0,
        description="Total telephone conversation length in seconds.",
    )
