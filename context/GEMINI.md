# Developer Coding Skills & Rules: Carrier Sales Agent PoC

## 1. Security Mandate (FastAPI Middlewares)
* **Rule:** Every active router in the `backend/` directory must be protected by an `X-API-KEY` validation interceptor.
* **Implementation:** Use FastAPI's `Security` or a custom dependency injection layer to validate headers against the local `API_KEY` environment variable. If missing or invalid, return an HTTP 401 Unauthorized status instantly.

## 2. Vetting Rules (`/validate-mc`)
* **Rule:** When parsing the response payload for a carrier's MC verification, compliance eligibility depends on two exact key-value conditions:
  1. `operating_status == "AUTHORIZED"`
  2. `active_insurance == true`
* **Fallback:** If either condition evaluates to false, return a payload declaring the carrier ineligible so HappyRobot can prompt a polite call termination loop.

## 3. Parametric Matching Logic (`/loads/search`)
* **Rule:** Enable flexible matching queries. The query parser must handle incoming optional arguments for `origin`, `destination`, and `equipment_type`.
* **Fallback Strategy:** If no record satisfies the strict combination of filters, write a query that falls back to matching only the `origin` and select the highest-paying load (`loadboard_rate`) available from that location to optimize freight conversion opportunities.

## 4. Negotiation Math Engine (`/negotiate`)
* **State Values:** Track state using `negotiation_round` (integers 1 to 3) passed as stateless payload context parameters.
* **Formula Coefficients:** * Max target tolerance percentage ($T_m$) = `0.10` (10% over base price).
  * Calculate maximum allowed counter-proposals ($M_i$) strictly using:
    $$M_i = \text{loadboard\_rate} \times \left(1 + \left(0.10 \times \frac{\text{negotiation\_round}}{3}\right)\right)$$
* **Routing Flags:**
  * If `counter_offer` <= $M_i$, return status `"BOOKED"`.
  * If `counter_offer` > $M_i$ and `negotiation_round` < 3, return status `"COUNTERED"` along with the exact value of $M_i$.
  * If `counter_offer` > $M_i$ and `negotiation_round` == 3, return status `"REJECTED_RATE"`.