"""Test script for FMCSA MC validation endpoint."""

import os
import httpx
import json
import sys
from typing import Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/validate-mc"
API_KEY = os.getenv("API_KEY", "").strip()

# Test cases
TEST_CASES = [
    {
        "name": "Test Case 1: Valid MC (should call FMCSA if key configured)",
        "carrier_mc": "123456",
        "expected_field": "eligible",
    },
    {
        "name": "Test Case 2: Another valid MC",
        "carrier_mc": "654321",
        "expected_field": "operating_status",
    },
    {
        "name": "Test Case 3: Non-existent MC (should return not eligible)",
        "carrier_mc": "999999999",
        "expected_field": "safety_rating",
    },
]


def test_validate_mc(carrier_mc: str) -> dict[str, Any] | None:
    """
    Call the /validate-mc endpoint.

    Args:
        carrier_mc: Motor Carrier number to validate.

    Returns:
        Response JSON or None if request failed.
    """
    url = f"{BASE_URL}{ENDPOINT}"
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"carrier_mc": carrier_mc}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            if response.status_code >= 400:
                print(f"Error: {response.text}")
                return None

            return response.json()

    except httpx.ConnectError:
        print(f"❌ Connection Error: Cannot connect to {BASE_URL}")
        print("   Make sure FastAPI server is running: `uvicorn main:app --reload`")
        return None
    except httpx.TimeoutException:
        print(f"❌ Timeout: Request took longer than 10 seconds")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__}: {e}")
        return None


def print_result(result: dict[str, Any]) -> None:
    """Pretty print result."""
    print("\nResponse:")
    print(json.dumps(result, indent=2))

    if result.get("eligible"):
        print("✅ Carrier is ELIGIBLE")
    else:
        print("❌ Carrier is NOT ELIGIBLE")


def main() -> None:
    """Run test suite."""
    print("=" * 70)
    print("FMCSA MC Validation Endpoint - Test Suite")
    print("=" * 70)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")

    print("\n" + "=" * 70)
    print("Prerequisites:")
    print("  1. FastAPI backend running: uvicorn main:app --reload")
    print("  2. FMCSA_API_KEY configured in .env")
    print("  3. Internet connection (to reach api.fmcsa.dot.gov)")
    print("=" * 70)

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: {test_case['name']}")
        print(f"{'─' * 70}")
        print(f"Request: POST {ENDPOINT}")
        print(f"Payload: {{'carrier_mc': '{test_case['carrier_mc']}'}}")

        result = test_validate_mc(test_case["carrier_mc"])

        if result:
            print_result(result)

            # Validate response structure
            expected_fields = ["eligible", "operating_status", "safety_rating"]
            missing_fields = [f for f in expected_fields if f not in result]

            if missing_fields:
                print(f"⚠️  Missing expected fields: {missing_fields}")
            else:
                print("✅ Response structure is correct")

        else:
            print("❌ Test failed - no valid response")

    print(f"\n{'=' * 70}")
    print("Test suite completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
