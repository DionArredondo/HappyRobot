"""FMCSA Vetting & Eligibility Router - Real carrier compliance verification."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


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
        description="Operating status from FMCSA: ACTIVE or INACTIVE.",
    )
    safety_rating: str | None = Field(
        default=None,
        description="Safety rating from FMCSA (SATISFACTORY, UNSATISFACTORY, or CONDITIONAL).",
    )


router = APIRouter(tags=["vetting"])

# Configuration
FMCSA_API_BASE = "https://api.fmcsa.dot.gov/v1"
FMCSA_TIMEOUT = 5.0  # seconds


def _get_fmcsa_api_key() -> str:
    """
    Retrieve FMCSA API Key from environment.

    Returns:
        API key string.

    Raises:
        HTTPException: If API key is not configured.
    """
    api_key = os.getenv("FMCSA_API_KEY", "").strip()
    if not api_key:
        logger.error("FMCSA_API_KEY not configured in environment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FMCSA API Key not configured. Please contact support.",
        )
    return api_key


def _fetch_carrier_data(carrier_mc: str, api_key: str) -> dict[str, Any] | None:
    """
    Fetch carrier data from FMCSA API.

    Args:
        carrier_mc: Motor Carrier number to look up.
        api_key: FMCSA API key.

    Returns:
        Parsed JSON response or None if not found/error.
    """
    url = f"{FMCSA_API_BASE}/carriers/mc/{carrier_mc}"
    params = {"apiKey": api_key}

    try:
        with httpx.Client(timeout=FMCSA_TIMEOUT) as client:
            response = client.get(url, params=params)

            # 404 means carrier not found
            if response.status_code == 404:
                logger.warning(f"Carrier MC {carrier_mc} not found in FMCSA database")
                return None

            # Other client errors should trigger fallback
            if 400 <= response.status_code < 500:
                logger.warning(
                    f"FMCSA API client error {response.status_code} for MC {carrier_mc}"
                )
                return None

            # Server errors should also fallback
            if response.status_code >= 500:
                logger.error(
                    f"FMCSA API server error {response.status_code} for MC {carrier_mc}"
                )
                return None

            # Success - parse and return
            if response.status_code == 200:
                return response.json()

    except httpx.TimeoutException:
        logger.error(f"FMCSA API timeout for MC {carrier_mc}")
        return None
    except httpx.RequestError as e:
        logger.error(f"FMCSA API connection error for MC {carrier_mc}: {e}")
        return None
    except ValueError as e:
        logger.error(f"FMCSA API invalid JSON response for MC {carrier_mc}: {e}")
        return None

    return None


def _evaluate_carrier_eligibility(carrier_data: dict[str, Any]) -> tuple[bool, str, str | None]:
    """
    Evaluate carrier eligibility based on FMCSA criteria.

    Criteria:
    1. allowedToOperate must be True or "Y"
    2. safetyRating must NOT be "UNSATISFACTORY"

    Args:
        carrier_data: FMCSA API response data.

    Returns:
        Tuple of (eligible: bool, operating_status: str, safety_rating: str | None)
    """
    # Check if allowed to operate
    allowed_to_operate = carrier_data.get("allowedToOperate")
    if isinstance(allowed_to_operate, bool):
        is_allowed = allowed_to_operate
    elif isinstance(allowed_to_operate, str):
        is_allowed = allowed_to_operate.upper() == "Y"
    else:
        is_allowed = False

    # Get safety rating
    safety_rating = carrier_data.get("safetyRating", "").strip().upper()

    # Evaluate eligibility: must be allowed AND not unsatisfactory
    is_eligible = is_allowed and safety_rating != "UNSATISFACTORY"

    # Map operating status
    operating_status = "ACTIVE" if is_allowed else "INACTIVE"

    return is_eligible, operating_status, safety_rating if safety_rating else None


@router.post(
    "/validate-mc",
    response_model=ValidateMCResponse,
    summary="Validate carrier MC number against FMCSA database",
    description="Performs real-time FMCSA verification on a carrier MC number. "
    "Returns eligibility status based on authorization and safety rating.",
)
def validate_mc(payload: ValidateMCRequest) -> ValidateMCResponse:
    """
    Validate a carrier's MC number against the real FMCSA database.

    Enforcement Criteria:
    1. Carrier must be allowed to operate (allowedToOperate = True or "Y")
    2. Carrier safety rating must NOT be "UNSATISFACTORY"

    Error Handling:
    - If FMCSA API is unreachable or times out, returns safe fallback (not eligible).
    - If API key is missing, returns 500 error.

    Args:
        payload: Request containing the carrier_mc string.

    Returns:
        ValidateMCResponse with eligibility, operating_status, and safety_rating fields.

    Raises:
        HTTPException: If FMCSA_API_KEY is not configured.
    """
    carrier_mc = payload.carrier_mc.strip()

    # Retrieve API key (raises HTTPException if not found)
    api_key = _get_fmcsa_api_key()

    # Fetch carrier data from FMCSA
    carrier_data = _fetch_carrier_data(carrier_mc, api_key)

    # Fallback: if fetch failed or returned None, return not eligible
    if carrier_data is None:
        logger.warning(f"Fallback: MC {carrier_mc} marked as ineligible due to API fetch failure")
        return ValidateMCResponse(
            eligible=False,
            operating_status="INACTIVE",
            safety_rating=None,
        )

    # Evaluate eligibility based on FMCSA criteria
    is_eligible, operating_status, safety_rating = _evaluate_carrier_eligibility(carrier_data)

    logger.info(
        f"MC {carrier_mc} vetting result: eligible={is_eligible}, "
        f"status={operating_status}, rating={safety_rating}"
    )

    return ValidateMCResponse(
        eligible=is_eligible,
        operating_status=operating_status,
        safety_rating=safety_rating,
    )
