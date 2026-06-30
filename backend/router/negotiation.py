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
    turn_count: int = Field(
        default=1,
        description="Negotiation turn number (1-3). Tracks progress through negotiation rounds.",
        ge=1,
        le=3,
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
    turn_count: int = Field(
        default=1,
        description="Current negotiation turn (1-3). Max 3 turns before forced rejection.",
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
    Evaluate a carrier's counter offer with multi-turn negotiation support (max 3 turns).
    
    Bot negotiation strategy - gradually lowers acceptable rate:
    - Turn 1: Bot proposes 97% of loadboard_rate
    - Turn 2: Bot proposes 95% of loadboard_rate
    - Turn 3: Bot proposes 90% of loadboard_rate (absolute minimum)
    
    Logic:
    - If counter_offer >= bot_proposal_for_current_turn: Status "ACCEPTED"
    - If counter_offer < bot_proposal_for_current_turn:
      * If turn_count < 3: Status "COUNTER" with next turn's lower proposal, turn_count++
      * If turn_count >= 3: Status "REJECTED" (no more negotiation rounds)

    Args:
        payload: Request containing load_id, counter_offer, and turn_count.

    Returns:
        NegotiateResponse with negotiation status, offer (or null), load_id, and updated turn_count.

    Raises:
        HTTPException 404: If the specified load_id does not exist.
        HTTPException 500: If database query fails.
    """
    load_id = payload.load_id.strip()
    counter_offer = payload.counter_offer
    turn_count = payload.turn_count

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

        # Define bot's proposals for each turn
        bot_proposals = {
            1: loadboard_rate * 0.97,  # Turn 1: 97% of baseline
            2: loadboard_rate * 0.95,  # Turn 2: 95% of baseline
            3: loadboard_rate * 0.90,  # Turn 3: 90% of baseline (absolute minimum)
        }

        # Get bot's proposal for current turn
        current_bot_proposal = bot_proposals.get(turn_count, loadboard_rate * 0.90)

        # Evaluate carrier's counter offer against bot's current proposal
        if counter_offer >= current_bot_proposal:
            # Carrier offer meets or exceeds bot's proposal: ACCEPT
            return NegotiateResponse(
                status="ACCEPTED",
                offer=counter_offer,
                load_id=load_id,
                turn_count=turn_count,
            )

        else:
            # Carrier offer is below bot's proposal
            if turn_count < 3:
                # More rounds available: make a lower counter-proposal for next turn
                next_turn = turn_count + 1
                next_bot_proposal = bot_proposals.get(next_turn, loadboard_rate * 0.90)
                return NegotiateResponse(
                    status="COUNTER",
                    offer=next_bot_proposal,
                    load_id=load_id,
                    turn_count=next_turn,
                )
            else:
                # Turn 3 complete: reject and close negotiation
                return NegotiateResponse(
                    status="REJECTED",
                    offer=None,
                    load_id=load_id,
                    turn_count=turn_count,
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
