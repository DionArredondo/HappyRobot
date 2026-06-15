"""Seed the Supabase ``loads`` table with mock freight records."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import supabase

MOCK_LOADS: list[dict[str, object]] = [
    {
        "load_id": "LD-001",
        "origin": "Chicago, IL",
        "destination": "Dallas, TX",
        "pickup_datetime": "2026-07-01T08:00:00Z",
        "delivery_datetime": "2026-07-02T18:00:00Z",
        "equipment_type": "Reefer",
        "loadboard_rate": 2850.00,
        "weight": 42000,
        "commodity_type": "Produce",
        "num_of_pieces": 24,
        "miles": 925,
        "dimensions": "48x8.5x9 ft",
        "notes": "Maintain 34-36F throughout transit.",
    },
    {
        "load_id": "LD-002",
        "origin": "Laredo, TX",
        "destination": "Atlanta, GA",
        "pickup_datetime": "2026-07-03T06:30:00Z",
        "delivery_datetime": "2026-07-04T22:00:00Z",
        "equipment_type": "Dry Van",
        "loadboard_rate": 3100.00,
        "weight": 38500,
        "commodity_type": "Consumer Goods",
        "num_of_pieces": 18,
        "miles": 1040,
        "dimensions": "53x8.5x9 ft",
        "notes": "No partial unloading.",
    },
    {
        "load_id": "LD-003",
        "origin": "Los Angeles, CA",
        "destination": "Phoenix, AZ",
        "pickup_datetime": "2026-07-02T14:00:00Z",
        "delivery_datetime": "2026-07-03T05:00:00Z",
        "equipment_type": "Flatbed",
        "loadboard_rate": 1450.00,
        "weight": 47000,
        "commodity_type": "Steel Coils",
        "num_of_pieces": 6,
        "miles": 370,
        "dimensions": "48x8 ft",
        "notes": "Tarps and chains required.",
    },
    {
        "load_id": "LD-004",
        "origin": "Memphis, TN",
        "destination": "Miami, FL",
        "pickup_datetime": "2026-07-05T09:00:00Z",
        "delivery_datetime": "2026-07-06T20:00:00Z",
        "equipment_type": "Reefer",
        "loadboard_rate": 2650.00,
        "weight": 40000,
        "commodity_type": "Frozen Seafood",
        "num_of_pieces": 32,
        "miles": 1015,
        "dimensions": "53x8.5x9 ft",
        "notes": "Keep at -10F; pre-cool trailer.",
    },
    {
        "load_id": "LD-005",
        "origin": "Denver, CO",
        "destination": "Kansas City, MO",
        "pickup_datetime": "2026-07-06T11:00:00Z",
        "delivery_datetime": "2026-07-07T07:30:00Z",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1750.00,
        "weight": 36000,
        "commodity_type": "Beverages",
        "num_of_pieces": 26,
        "miles": 605,
        "dimensions": "48x8.5x9 ft",
        "notes": None,
    },
    {
        "load_id": "LD-006",
        "origin": "Seattle, WA",
        "destination": "Portland, OR",
        "pickup_datetime": "2026-07-04T07:00:00Z",
        "delivery_datetime": "2026-07-04T15:00:00Z",
        "equipment_type": "Flatbed",
        "loadboard_rate": 980.00,
        "weight": 44500,
        "commodity_type": "Lumber",
        "num_of_pieces": 12,
        "miles": 175,
        "dimensions": "48x8 ft",
        "notes": "Driver assist unload at yard gate 3.",
    },
    {
        "load_id": "LD-007",
        "origin": "Houston, TX",
        "destination": "New Orleans, LA",
        "pickup_datetime": "2026-07-08T05:00:00Z",
        "delivery_datetime": "2026-07-08T16:00:00Z",
        "equipment_type": "Reefer",
        "loadboard_rate": 1325.00,
        "weight": 39000,
        "commodity_type": "Dairy",
        "num_of_pieces": 20,
        "miles": 348,
        "dimensions": "48x8.5x9 ft",
        "notes": "Appointment required for delivery.",
    },
    {
        "load_id": "LD-008",
        "origin": "Indianapolis, IN",
        "destination": "Charlotte, NC",
        "pickup_datetime": "2026-07-09T10:00:00Z",
        "delivery_datetime": "2026-07-10T12:00:00Z",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1980.00,
        "weight": 37200,
        "commodity_type": "Auto Parts",
        "num_of_pieces": 14,
        "miles": 585,
        "dimensions": "53x8.5x9 ft",
        "notes": "Liftgate not required.",
    },
    {
        "load_id": "LD-009",
        "origin": "Salt Lake City, UT",
        "destination": "Boise, ID",
        "pickup_datetime": "2026-07-07T13:00:00Z",
        "delivery_datetime": "2026-07-08T02:00:00Z",
        "equipment_type": "Flatbed",
        "loadboard_rate": 1125.00,
        "weight": 46000,
        "commodity_type": "Construction Materials",
        "num_of_pieces": 8,
        "miles": 340,
        "dimensions": "48x8 ft",
        "notes": "Oversize permits included by shipper.",
    },
    {
        "load_id": "LD-010",
        "origin": "Nashville, TN",
        "destination": "Jacksonville, FL",
        "pickup_datetime": "2026-07-11T08:30:00Z",
        "delivery_datetime": "2026-07-12T19:00:00Z",
        "equipment_type": "Reefer",
        "loadboard_rate": 2280.00,
        "weight": 41500,
        "commodity_type": "Pharmaceuticals",
        "num_of_pieces": 16,
        "miles": 655,
        "dimensions": "53x8.5x9 ft",
        "notes": "Temperature log required at delivery.",
    },
    {
        "load_id": "LD-011",
        "origin": "Chicago, IL",
        "destination": "Detroit, MI",
        "pickup_datetime": "2026-07-12T06:00:00Z",
        "delivery_datetime": "2026-07-12T14:30:00Z",
        "equipment_type": "Dry Van",
        "loadboard_rate": 890.00,
        "weight": 33000,
        "commodity_type": "Paper Products",
        "num_of_pieces": 22,
        "miles": 280,
        "dimensions": "48x8.5x9 ft",
        "notes": "FCFS pickup and delivery windows.",
    },
    {
        "load_id": "LD-012",
        "origin": "Laredo, TX",
        "destination": "San Antonio, TX",
        "pickup_datetime": "2026-07-13T04:00:00Z",
        "delivery_datetime": "2026-07-13T11:00:00Z",
        "equipment_type": "Flatbed",
        "loadboard_rate": 760.00,
        "weight": 43500,
        "commodity_type": "Machinery",
        "num_of_pieces": 4,
        "miles": 155,
        "dimensions": "48x8 ft",
        "notes": None,
    },
]


def seed_loads() -> None:
    """Insert mock freight loads into Supabase."""
    try:
        response = supabase.table("loads").insert(MOCK_LOADS).execute()
        inserted_count = len(response.data) if response.data else len(MOCK_LOADS)
        print(
            f"Success: seeded {inserted_count} freight load record(s) into the 'loads' table."
        )
    except Exception as exc:
        print(f"Error: failed to seed loads table. {exc}")


if __name__ == "__main__":
    seed_loads()
