# HappyRobot Inbound Freight Broker Agent - PoC

This repository contains the complete Proof of Concept (PoC) for an automated inbound carrier voice agent built for **Acme Logistics** using the HappyRobot platform and a custom FastAPI orchestration engine.

## Quick Start with Docker

1. Clone the repository.
2. Create your `.env` files in both `/backend` and `/frontend` folders using the required keys (`API_KEY`, `FMCSA_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`).
3. Run the entire infrastructure with a single command:
   ```bash
   docker-compose up --build