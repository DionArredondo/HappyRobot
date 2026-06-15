"""Price Negotiation Router - Dynamic rate negotiation engine with acceptance thresholds."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database import supabase


class NegotiateRequest(BaseModel):
    """Request payload for price negotiation."""

    load_id: str = Field(
        ...,
        description="Unique load identifier to negotiate on.",
        min_length=1,
    )
    counter_offer: float = Field(
        ...,
        description="Carrier's counter offer price for the load.",
        gt=0,
    )


class NegotiateResponse(BaseModel):
    """Response payload from price negotiation evaluation."""

    status: str = Field(
        ...,
        description="Negotiation outcome: ACCEPTED, COUNTER, or REJECTED.",
    )
    offer: Optional[float] = Field(
        default=None,
        description="Final negotiated rate or system counter-proposal. Null if rejected.",
    )
    load_id: str = Field(
        ...,
        description="The load_id being negotiated.",
    )


router = APIRouter(tags=["negotiation"])


@router.post(
    "/negotiate",
    response_model=NegotiateResponse,
    summary="Evaluate counter offer and return negotiation status",
    description="Analyzes a carrier's counter offer against the baseline load rate. "
    "Returns acceptance, rejection, or system counter-proposal.",
)
def negotiate(payload: NegotiateRequest) -> NegotiateResponse:
    """
    Evaluate a carrier's counter offer against the load's baseline rate.

    Evaluation Logic:
    - If counter_offer <= loadboard_rate: Status "ACCEPTED" with final rate = counter_offer.
    - If counter_offer > (loadboard_rate * 1.15): Status "REJECTED" with offer = null (exceeds 15% threshold).
    - If between rate and ceiling: Status "COUNTER" with system proposal = (loadboard_rate + counter_offer) / 2.

    Args:
        payload: Request containing load_id and counter_offer.

    Returns:
        NegotiateResponse with negotiation status, offer (or null), and load_id.

    Raises:
        HTTPException 404: If the specified load_id does not exist.
        HTTPException 500: If database query fails.
    """
    load_id = payload.load_id.strip()
    counter_offer = payload.counter_offer

    try:
        # Query Supabase for the specific load
        result = (
            supabase.table("loads")
            .select("loadboard_rate")
            .eq("load_id", load_id)
            .execute()
        )

        loads = result.data

        if not loads:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Load not found: {load_id}",
            )

        loadboard_rate = loads[0]["loadboard_rate"]

        # Evaluation threshold: 15% ceiling above baseline
        ceiling_rate = loadboard_rate * 1.15

        # Determine negotiation status based on counter_offer vs thresholds
        if counter_offer <= loadboard_rate:
            # Offer is at or below baseline: ACCEPTED
            return NegotiateResponse(
                status="ACCEPTED",
                offer=counter_offer,
                load_id=load_id,
            )

        elif counter_offer > ceiling_rate:
            # Offer exceeds 15% ceiling: REJECTED
            return NegotiateResponse(
                status="REJECTED",
                offer=None,
                load_id=load_id,
            )

        else:
            # Offer is within acceptable range: propose average as counter
            system_counter = (loadboard_rate + counter_offer) / 2
            return NegotiateResponse(
                status="COUNTER",
                offer=system_counter,
                load_id=load_id,
            )

    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except Exception as e:
        # Catch database or unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Negotiation evaluation error: {str(e)}",
        ) from e
