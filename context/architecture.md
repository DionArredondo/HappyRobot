# Architectural Blueprint: Inbound Carrier Sales Agent Automation (PoC)

## 1. Executive Summary
This document details the software architecture, data contracts, and business logic for an automated AI-driven Voice Agent designed to handle inbound carrier sales calls for a freight brokerage. The solution automates caller vetting via regulatory compliance APIs, matches carrier capacity with real-time available freight, executes programmatic rate negotiations, and logs comprehensive performance analytics into a dedicated stakeholder dashboard.

## 2. High-Level Architecture & System Boundaries
The platform relies on a decoupled, asynchronous architecture where the **HappyRobot Voice Engine** manages telephony, Automated Speech Recognition (ASR), and Text-to-Speech (TTS), while a custom **FastAPI Backend** serves as the stateless decision-making engine and tool provider.

+-------------------+        Audio Stream        +----------------------+
|   Carrier Phone   | <========================> | HappyRobot AI Engine |
|  (Browser Audio)  |                            | (Voice/Context Layer)|
+-------------------+                            +----------+-----------+
                                                            |
                                                            | HTTPS Hooks
                                                            | (Secured via API Key)
                                                            v
+-------------------+        Read / Write        +----------------------+
|  Streamlit Dash   | <========================> | FastAPI Backend Core |
|  (BI Analytics)   |                            | (Business Logic/Tool)|
+-------------------+                            +-----┬----------┬-----+
                                                       |          |
                                            Read/Write |          | HTTPS Client
                                                       v          v
                                                 +-----+----+ +---+------+
                                                 | Supabase | |  FMCSA   |
                                                 | Postgres | | Gov API  |
                                                 +----------+ +----------+

### Components:
1. **HappyRobot Platform:** Controls the live conversation loop using custom System Prompts and triggers outbound HTTPS tool calls.
2. **FastAPI Backend (Python):** Contains core algorithmic routers (`/validate-mc`, `/loads/search`, `/negotiate`, `/webhooks/call-ended`).
3. **Supabase (PostgreSQL):** Stores institutional data including current open loads and downstream call analytics tracking.
4. **Streamlit (Frontend Dashboard):** Evaluates brokerage operations performance, conversion metrics, and financial outcomes.

---

## 3. Design Decisions & Technical Trade-offs
* **FastAPI + Supabase vs. Local File Storage:** To satisfy the prompt's option of using a file or a database, we selected a relational database (Supabase PostgreSQL). This choice ensures ACID compliance, allows structured filtering for load matching, and prevents state loss during concurrent carrier calls.
* **Ngrok TLS Tunneling for Local Development:**
  The challenge mandates HTTPS endpoints and basic security features. Since local development environments (`localhost`) cannot easily provision valid CA-signed SSL certificates, we integrated `ngrok` as a secure reverse-proxy. This satisfies HappyRobot's production webhook requirements without adding local credential friction.
* **Stateless Multi-Round Negotiation:**
  To maintain a clean microservices architecture, the backend does not store session state in memory. Instead, the current negotiation round count is handled as a conversational parameter passed back and forth within HappyRobot's voice context.


## 3. Core Business Logic & Algorithms

### A. Vetting & Eligibility Workflow (`/validate-mc`)
When a carrier provides their Motor Carrier (MC) number, the backend queries the Federal Motor Carrier Safety Administration (FMCSA) API. 
* **Rule:** A carrier is authorized to book a load *only* if their operating status equals `"AUTHORIZED"` and they have active insurance on file. If validation fails, the API instructs HappyRobot to gracefully terminate the call.

### B. Parametric Load Matching (`/loads/search`)
The agent extracts search constraints spoken by the carrier. The API queries the database utilizing dynamic SQL filtering matching:
$$\text{Query Filters} = \{\text{origin}, \text{destination}, \text{equipment\_type}\}$$
If an exact match is missing, the API implements a fallback strategy returning the highest-paying load departing from that specific origin to ensure conversion is maximized.

### C. 3-Round Rate Negotiation Algorithm (`/negotiate`)
Negotiations operate as a Bounded State Machine to eliminate LLM pricing hallucinations and maintain healthy profit margins.

* **Definitions:**
  * $R_b$: `loadboard_rate` (The initial advertised price).
  * $C_o$: `counter_offer` (The price requested by the carrier).
  * $T_m$: Max total tolerance percentage allocated for the load (e.g., `0.10` or `10%`).
  * $i$: `negotiation_round` (State tracker passed dynamically between loops, from 1 to 3).

* **Max Allowed Offer Formula per Round ($M_i$):**
  The maximum price the bot can offer increases incrementally per round:
  $$M_i = R_b \times \left(1 + \left(T_m \times \frac{i}{3}\right)\right)$$

* **Decision Tree Logic:**
  1. If $C_o \le M_i$: The backend accepts the offer immediately. The state is updated to `BOOKED` and a success response is returned to execute a simulated transfer.
  2. If $C_o > M_i$ AND $i < 3$: The backend rejects $C_o$ and counters back with exactly $M_i$. The voice state increments $i \to i + 1$ for the next iteration.
  3. If $C_o > M_i$ AND $i = 3$: The negotiation fails. The state updates to `REJECTED_RATE` and the bot wraps up the call without booking.

---

## 4. Operational Telemetry & Post-Call Processing
Upon call teardown, HappyRobot dispatches a summary payload to `/webhooks/call-ended`. The backend extracts:
* **Call Outcome Status:** Structured as `BOOKED`, `REJECTED_RATE`, `VETTING_FAILED`, or `HUNG_UP`.
* **Financial Metrics:** Computes the delta ($\Delta = \text{Final Agreed Rate} - \text{Original Rate}$) to measure gross profit impacts.
* **Sentiment Metrics:** Logs carrier attitude classifications (`positive`, `neutral`, `negative`) for carrier relations evaluation.

---

## 5. Security & Infrastructure Controls
* **Authentication:** Middleware intercepts all inbound requests to the FastAPI backend, enforcing validation of an `X-API-KEY` header token.
* **Network Security:** Local environments leverage `ngrok` TLS tunnels. Production networks enforce end-to-end encryption via Automated Let's Encrypt SSL/HTTPS terminations.
* **Deployment Topology:** Multicontainer orchestration is configured via `docker-compose.yml`. Production deployment runs isolated Linux containers hosted on a scalable PaaS cloud topology (Railway).