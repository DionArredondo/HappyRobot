"""FMCSA Vetting & Eligibility Router - Mock verification client for carrier compliance."""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter


class ValidateMCRequest(BaseModel):
    """Request payload for MC number validation."""

    carrier_mc: str = Field(
        ...,
        description="Motor Carrier (MC) number string to validate.",
        min_length=1,
        max_length=50,
    )


class ValidateMCResponse(BaseModel):
    """Response payload from FMCSA vetting check."""

    eligible: bool = Field(
        ...,
        description="Whether the carrier meets eligibility criteria.",
    )
    operating_status: str = Field(
        ...,
        description="Operating status from FMCSA: AUTHORIZED or NOT_AUTHORIZED.",
    )
    active_insurance: bool = Field(
        ...,
        description="Whether the carrier has active insurance coverage.",
    )


router = APIRouter(tags=["vetting"])


@router.post(
    "/validate-mc",
    response_model=ValidateMCResponse,
    summary="Validate carrier MC number against FMCSA database",
    description="Performs mock FMCSA verification on a carrier MC number. "
    "Returns eligibility status, operating authorization, and insurance coverage.",
)
def validate_mc(payload: ValidateMCRequest) -> ValidateMCResponse:
    """
    Validate a carrier's MC number against mock FMCSA database.

    Mock Verification Logic:
    - If carrier_mc is "MC-999999" (failure test case), simulate compliance failure.
    - For any other valid MC number, simulate successful compliance check.

    Enforcement Criteria:
    - Both operating_status == "AUTHORIZED" AND active_insurance == true are required.

    Args:
        payload: Request containing the carrier_mc string.

    Returns:
        ValidateMCResponse with eligibility, operating_status, and active_insurance fields.
    """
    carrier_mc = payload.carrier_mc.strip()

    # Mock failure case: simulate compliance check failure
    if carrier_mc == "MC-999999":
        return ValidateMCResponse(
            eligible=False,
            operating_status="NOT_AUTHORIZED",
            active_insurance=False,
        )

    # Default case: simulate successful compliance check
    return ValidateMCResponse(
        eligible=True,
        operating_status="AUTHORIZED",
        active_insurance=True,
    )
