"""Call Logs Router - Structured post-call operational metrics persistence."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database import supabase


class CallLogRequest(BaseModel):
    """Request payload for call log submission from HappyRobot."""

    call_id: str = Field(
        ...,
        description="Unique call identifier from HappyRobot.",
        min_length=1,
    )
    carrier_mc: str = Field(
        ...,
        description="Motor Carrier identifier evaluated during the call.",
        min_length=1,
    )
    load_id: Optional[str] = Field(
        default=None,
        description="Foreign key referencing loads.load_id (nullable if no load was booked).",
    )
    final_rate: Optional[float] = Field(
        default=None,
        description="Agreed settlement price (nullable if outcome is not BOOKED).",
        gt=0,
    )
    outcome: str = Field(
        ...,
        description="Structured call disposition status (e.g., BOOKED, REJECTED_RATE, VETTING_FAILED, HUNG_UP).",
        min_length=1,
    )
    sentiment: str = Field(
        ...,
        description="Carrier attitude classification (e.g., POSITIVE, NEUTRAL, NEGATIVE).",
        min_length=1,
    )
    duration_seconds: int = Field(
        ...,
        description="Total telephone conversation length in seconds.",
        ge=0,
    )


class CallLogResponse(BaseModel):
    """Response payload confirming successful call log insertion."""

    status: str = Field(
        ...,
        description="Operation status indicator.",
    )
    call_id: str = Field(
        ...,
        description="The call_id that was logged.",
    )


router = APIRouter(tags=["call_logs"])


@router.post(
    "/call-logs",
    response_model=CallLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log post-call operational metrics",
    description="Persists call outcome, carrier sentiment, and negotiation results to the call_logs table. "
    "Returns HTTP 201 Created on successful insertion.",
)
def create_call_log(payload: CallLogRequest) -> CallLogResponse:
    """
    Submit and persist a structured call log entry to the database.

    Accepts post-call metrics including call outcome, carrier sentiment, duration,
    and optional load/rate information if a transaction was booked. Persists the
    complete payload to the "call_logs" Supabase table and returns confirmation.

    Args:
        payload: CallLogRequest with required and optional call metrics.

    Returns:
        CallLogResponse confirming successful logging with call_id.

    Raises:
        HTTPException 500: If database insertion fails.
    """
    try:
        # Prepare the payload for database insertion
        log_data = {
            "call_id": payload.call_id.strip(),
            "carrier_mc": payload.carrier_mc.strip(),
            "load_id": payload.load_id,
            "final_rate": payload.final_rate,
            "outcome": payload.outcome.strip(),
            "sentiment": payload.sentiment.strip(),
            "duration_seconds": payload.duration_seconds,
        }

        # Insert the call log into Supabase "call_logs" table
        result = supabase.table("call_logs").insert(log_data).execute()

        # Verify insertion was successful
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Call log insertion failed: no data returned from database.",
            )

        return CallLogResponse(
            status="logged",
            call_id=payload.call_id,
        )

    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except Exception as e:
        # Catch database or unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log call: {str(e)}",
        ) from e
