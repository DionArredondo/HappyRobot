"""Load Matching Router - Dynamic query filtering with intelligent fallback logic."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, status

from database import supabase
from models import LoadModel


router = APIRouter(tags=["matching"])


@router.get(
    "/loads/search",
    response_model=list[LoadModel] | LoadModel,
    summary="Search loads with intelligent fallback matching",
    description="Query the loads table by optional filters (origin, destination, equipment_type). "
    "If no exact matches found, automatically falls back to return the highest-paying load by origin.",
)
def search_loads(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
) -> list[LoadModel] | LoadModel:
    """
    Search for freight loads with relational filtering and fallback logic.

    Primary Query:
    - Filters by all provided parameters (origin, destination, equipment_type).
    - Returns list of matching loads if any are found.

    Fallback Query (CRITICAL):
    - If primary query returns empty, instantly triggers fallback filtering by origin ONLY.
    - Orders results by loadboard_rate in descending order.
    - Returns the single highest-paying load to maximize carrier asset conversion.

    Args:
        origin: Optional pickup location (city/state).
        destination: Optional delivery location (city/state).
        equipment_type: Optional required equipment type (e.g., Reefer, Dry Van).

    Returns:
        List of LoadModel objects if multiple matches found, or single LoadModel for fallback result.

    Raises:
        HTTPException 400: If origin not provided for fallback search.
        HTTPException 404: If no loads found even after fallback.
    """
    try:
        # Build primary query with all provided filters
        query = supabase.table("loads").select("*")

        if origin:
            query = query.eq("origin", origin)
        if destination:
            query = query.eq("destination", destination)
        if equipment_type:
            query = query.eq("equipment_type", equipment_type)

        primary_result = query.execute()
        primary_loads = primary_result.data

        # If primary query returns results, return them
        if primary_loads:
            return [LoadModel(**load) for load in primary_loads]

        # FALLBACK: Primary query returned empty list
        # Query by origin only, ordered by highest rate
        if not origin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fallback search requires 'origin' parameter. "
                "Provide origin or refine your primary search criteria.",
            )

        fallback_result = (
            supabase.table("loads")
            .select("*")
            .eq("origin", origin)
            .order("loadboard_rate", desc=True)
            .limit(1)
            .execute()
        )

        fallback_loads = fallback_result.data

        if not fallback_loads:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No loads available for origin: {origin}",
            )

        # Return single highest-paying load from fallback query
        return LoadModel(**fallback_loads[0])

    except HTTPException:
        # Re-raise HTTPException as-is (for 400/404 above)
        raise
    except Exception as e:
        # Catch database or parsing errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Load search error: {str(e)}",
        ) from e
