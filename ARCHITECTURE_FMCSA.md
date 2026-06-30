# 🏗️ Arquitectura de FMCSA Integration

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   HappyRobot Frontend                           │
│                    (app.py / React)                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ HTTP Request
                      │ "Validate Carrier MC-123456"
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   HappyRobot Backend (FastAPI)                  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  main.py - FastAPI Application                         │    │
│  │  - API Key Validation Middleware                       │    │
│  │  - CORS Configuration                                  │    │
│  │  - Router Registration                                 │    │
│  └────────────┬────────────────────────────────────────┬──┘    │
│               │                                        │         │
│  ┌────────────▼──────────────┐      ┌─────────────────▼─────┐  │
│  │ router/vetting.py ✨ NEW │      │ router/negotiation.py │  │
│  │ (FMCSA Integration)      │      │ (Call Handler)        │  │
│  │                          │      │                       │  │
│  │ POST /validate-mc ────────┼─────────────────┐          │  │
│  │ validate_mc()            │      │           │          │  │
│  │                          │      │           │          │  │
│  │ Functions:               │      ├──────────────────────┤  │
│  │ ├─ _get_fmcsa_api_key()  │      │ Calls vetting logic  │  │
│  │ ├─ _fetch_carrier_data() │      │ to check eligibility │  │
│  │ └─ _evaluate_carrier_eligibility()       │  │
│  │                          │      │                       │  │
│  └──────────────┬───────────┘      └───────────────────────┘  │
│                 │                                              │
│                 │ Load environment: FMCSA_API_KEY              │
│                 │ (from .env via python-dotenv)               │
│                 ▼                                              │
│  ┌────────────────────────────────────────────────────────┐   │
│  │         .env Configuration File                        │   │
│  │  FMCSA_API_KEY=your-actual-api-key-here             │   │
│  │  API_KEY=TU_API_KEY  │   │
│  │  SUPABASE_URL=https://...                            │   │
│  │  SUPABASE_KEY=...                                    │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ HTTP GET with API Key + Timeout (5s)
                      │ GET https://api.fmcsa.dot.gov/v1/carriers/mc/{MC}
                      │      ?apiKey={FMCSA_API_KEY}
                      ▼
        ┌─────────────────────────────────┐
        │  FMCSA Federal API               │
        │  (U.S. Motor Carrier Safety DB)  │
        │                                 │
        │  Returns:                       │
        │  {                              │
        │    "allowedToOperate": true,    │
        │    "safetyRating": "SATISF...", │
        │    ...more fields...            │
        │  }                              │
        └─────────────────────────────────┘
                      │
                      │ JSON Response (200 OK) or Error
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Backend Processing                            │
│                                                                 │
│  Evaluate FMCSA Criteria:                                      │
│  ✅ Is allowedToOperate == True?                              │
│  ✅ Is safetyRating != "UNSATISFACTORY"?                      │
│                                                                 │
│  Result Logic:                                                 │
│  ├─ Both True  → eligible=true, status="ACTIVE"               │
│  ├─ Any False  → eligible=false, status="INACTIVE"            │
│  └─ API Error  → eligible=false (FALLBACK SEGURO)             │
│                                                                 │
│  Return: ValidateMCResponse                                    │
│  {                                                             │
│    "eligible": true/false,                                     │
│    "operating_status": "ACTIVE"/"INACTIVE",                    │
│    "safety_rating": "SATISFACTORY"/null                        │
│  }                                                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ HTTP Response (200 OK)
                              ▼
                ┌─────────────────────────────────┐
                │  Frontend Display                │
                │  Carrier Eligibility Result      │
                │                                 │
                │ ✅ Eligible → Continue Negotiation
                │ ❌ Not Eligible → End Call      │
                └─────────────────────────────────┘
```

---

## Data Flow - Request/Response

### Request

```http
POST /validate-mc HTTP/1.1
Host: localhost:8000
X-API-KEY: TU_API_KEY
Content-Type: application/json

{
  "carrier_mc": "123456"
}
```

### Processing Steps

```
1. Validate X-API-KEY header (main.py middleware)
2. Parse ValidateMCRequest payload
3. Extract FMCSA_API_KEY from .env
4. Call httpx.Client.get() to FMCSA with 5s timeout
5. Handle response:
   - 200 OK → Parse JSON, evaluate criteria
   - 404    → Not found → eligible=false
   - 5xx    → Error → eligible=false (fallback)
   - Timeout → No response → eligible=false (fallback)
6. Return ValidateMCResponse JSON
```

### Response

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "eligible": true,
  "operating_status": "ACTIVE",
  "safety_rating": "SATISFACTORY"
}
```

---

## File Structure

```
HappyRobot/
├── .env                           ← FMCSA_API_KEY configured here
├── FMCSA_INTEGRATION.md           ← Configuration guide
├── CHANGES_SUMMARY.md             ← This document
│
└── backend/
    ├── main.py                    ← FastAPI app (unchanged)
    ├── models.py                  ← Pydantic models
    ├── database.py                ← Supabase connection
    ├── requirements.txt           ← Dependencies (httpx included)
    │
    ├── router/
    │   ├── vetting.py             ← ✨ REFACTORED (FMCSA integration)
    │   ├── negotiation.py         ← Calls vetting.validate_mc()
    │   ├── matching.py            ← Load matching logic
    │   └── call_logs.py           ← Call logging
    │
    └── test_vetting.py            ← ✨ NEW (Integration tests)
```

---

## Sequence Diagram - Happy Path

```
Frontend         Backend         FMCSA API
   │                │                │
   │─POST /validate-mc───────────────▶ │
   │                │                │
   │                ├─ Load FMCSA_API_KEY from .env
   │                │                │
   │                │─ GET /carriers/mc/123456 ────────────▶│
   │                │                 │
   │                │                 │ Lookup in database
   │                │◀─ 200 OK (JSON response)────────────  │
   │                │                │
   │                ├─ Parse JSON
   │                ├─ Check allowedToOperate
   │                ├─ Check safetyRating
   │                ├─ Evaluate eligibility
   │                │
   │◀────── 200 OK (ValidateMCResponse) ───────────────────│
   │                │                │
   ├─ Display result
   │                │                │
```

---

## Sequence Diagram - Error Handling Path

```
Frontend         Backend         FMCSA API
   │                │                │
   │─POST /validate-mc───────────────▶ │
   │                │                │
   │                ├─ Load FMCSA_API_KEY from .env
   │                │                │
   │                │─ GET /carriers/mc/999999 ──────────▶│
   │                │                 │
   │                │                 │ Not found
   │                │◀─ 404 Not Found──────────────────  │
   │                │                │
   │                ├─ FALLBACK: eligible=false
   │                │
   │◀────── 200 OK {eligible: false} ───────────────────│
   │                │                │
```

---

## Error Scenarios & Fallback

| Scenario | Expected Behavior | HTTP Code | Response |
|----------|-------------------|-----------|----------|
| Valid eligible carrier | Return full data | 200 | `{eligible: true, ...}` |
| Valid ineligible carrier | Return full data | 200 | `{eligible: false, ...}` |
| MC not found (404) | Fallback safe | 200 | `{eligible: false, status: INACTIVE}` |
| FMCSA server error (5xx) | Fallback safe | 200 | `{eligible: false, status: INACTIVE}` |
| Connection timeout (>5s) | Fallback safe | 200 | `{eligible: false, status: INACTIVE}` |
| Connection refused | Fallback safe | 200 | `{eligible: false, status: INACTIVE}` |
| API Key missing | Explicit error | 500 | `{detail: "API Key not configured"}` |
| API Key invalid | Fallback safe | 200 | `{eligible: false, status: INACTIVE}` |

**Key insight:** Only missing API Key returns 500. All other errors fallback to `eligible=false` without interrupting the voice call.

---

## Performance Characteristics

### Latency

```
┌──────────────────────────────────────┐
│         Request Timing               │
├──────────────────────────────────────┤
│ Parse JSON payload:          ~0 ms   │
│ Load FMCSA_API_KEY:          ~1 ms   │
│ HTTP GET to FMCSA:       1000-3000 ms│  ← Network latency
│ Parse FMCSA JSON:            ~2 ms   │
│ Evaluate criteria:           ~1 ms   │
│ Return response:             ~1 ms   │
├──────────────────────────────────────┤
│ Total (good network):   1005-3010 ms │
│ Total (slow network):   3000-5000 ms │  ← Max timeout
│ Total (timeout):           5000 ms   │  ← Fallback
└──────────────────────────────────────┘
```

### Network Usage

- **Request size**: ~100 bytes (JSON)
- **Response size**: ~500 bytes (FMCSA data)
- **Per validation**: ~0.6 KB
- **For 1000 validations**: ~600 KB

---

## Security Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Security Layers                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Layer 1: API Key Authentication (X-API-KEY header)       │
│  ├─ Validated in main.py middleware                       │
│  ├─ Prevents unauthorized access to /validate-mc          │
│  └─ Stored securely in .env (gitignored)                 │
│                                                            │
│  Layer 2: FMCSA API Key (Environment Variable)            │
│  ├─ Loaded from .env at startup                           │
│  ├─ Validated before use (raise 500 if missing)           │
│  ├─ NEVER logged or exposed in responses                  │
│  └─ Separated from frontend API key                       │
│                                                            │
│  Layer 3: HTTPS to FMCSA                                  │
│  ├─ All communication encrypted                           │
│  ├─ Prevents MitM attacks                                 │
│  └─ SSL certificate validation automatic with httpx       │
│                                                            │
│  Layer 4: Timeout Protection                              │
│  ├─ 5 second timeout prevents resource exhaustion         │
│  ├─ Prevents slowloris attacks                            │
│  └─ Enables safe fallback behavior                        │
│                                                            │
│  Layer 5: Error Masking                                   │
│  ├─ Generic errors returned to client                     │
│  ├─ Detailed errors logged server-side only               │
│  └─ No API internals leaked                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Monitoring & Logging

### Logs Emitted

```python
logger.info(  # Success
    "MC 123456 vetting result: eligible=true, status=ACTIVE, rating=SATISFACTORY"
)

logger.warning(  # Non-critical issues
    "Carrier MC 123456 not found in FMCSA database"
)

logger.error(  # Critical issues
    "FMCSA_API_KEY not configured in environment"
    "FMCSA API timeout for MC 123456"
    "FMCSA API connection error for MC 123456: Connection refused"
)
```

### Monitoring Metrics (Optional - Future)

```
✅ Total validations
✅ Successful FMCSA lookups
✅ Eligible carriers (true/false split)
✅ Average latency
✅ Error rate
✅ Timeout rate
✅ Fallback rate
```

Suggested tools:
- **Prometheus** for metrics collection
- **Grafana** for dashboards
- **ELK Stack** (Elasticsearch, Logstash, Kibana) for centralized logging

---

## Dependencies & Requirements

### Python Packages

```
fastapi          ← Web framework
uvicorn          ← ASGI server
pydantic         ← Data validation
httpx            ← HTTP client (used for FMCSA calls) ✨
python-dotenv    ← Environment variable loading
supabase         ← Database (unused in vetting)
```

### External APIs

| API | Purpose | Endpoint | Timeout |
|-----|---------|----------|---------|
| FMCSA | Carrier validation | `https://api.fmcsa.dot.gov/v1/carriers/mc/{mc}` | 5s |

### Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `FMCSA_API_KEY` | `.env` | Authentication to FMCSA API ✨ NEW |
| `API_KEY` | `.env` | Authentication for /validate-mc endpoint |
| `SUPABASE_URL` | `.env` | Database connection |
| `SUPABASE_KEY` | `.env` | Database authentication |

---

## Testing Strategy

### Unit Tests (Recommended Future)

```python
def test_get_fmcsa_api_key_missing():
    # Should raise HTTPException 500

def test_fetch_carrier_data_404():
    # Should return None

def test_evaluate_carrier_eligibility_satisfied():
    # Should return (True, "ACTIVE", "SATISFACTORY")

def test_evaluate_carrier_eligibility_unsatisfactory():
    # Should return (False, "INACTIVE", "UNSATISFACTORY")
```

### Integration Tests (Available)

Run `backend/test_vetting.py` to:
- Call actual endpoint
- Verify response structure
- Test with real MC numbers
- Check for connectivity issues

### Manual Testing

```bash
curl -X POST http://localhost:8000/validate-mc \
  -H "X-API-KEY: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"carrier_mc": "123456"}'
```

---

## Deployment Checklist

- [ ] FMCSA_API_KEY configured in production `.env`
- [ ] httpx library included in production requirements.txt
- [ ] HTTPS enabled for all communication
- [ ] Error logging configured
- [ ] Network connectivity to api.fmcsa.dot.gov verified
- [ ] Firewall/proxy rules allow outbound HTTPS
- [ ] Rate limiting implemented (if needed)
- [ ] Monitoring/alerting set up
- [ ] Load testing performed
- [ ] Fallback behavior tested

---

**Last Updated:** 2026-06-15  
**Status:** ✅ Ready for Integration
