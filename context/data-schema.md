# Database & Pydantic Data Contract Specs

## 1. Freight Loads Schema (`loads` Table)
Maps directly to the required fields for the available freight tracking dataset.

| Field Name | Type (DB / Pydantic) | Constraints / Description |
| :--- | :--- | :--- |
| `load_id` | TEXT / str | Primary Key. Unique identifier  |
| `origin` | TEXT / str | Starting location city/state  |
| `destination` | TEXT / str | Delivery location city/state  |
| `pickup_datetime` | TIMESTAMPTZ / datetime| Date and time for pickup  |
| `delivery_datetime`| TIMESTAMPTZ / datetime| Date and time for delivery  |
| `equipment_type` | TEXT / str | Type of equipment needed (e.g., Reefer)  |
| `loadboard_rate` | NUMERIC / float | Listed baseline rate for the load  |
| `weight` | NUMERIC / float | Load weight in lbs  |
| `commodity_type` | TEXT / str | Type of goods  |
| `num_of_pieces` | INTEGER / int | Number of physical items |
| `miles` | NUMERIC / float | Distance to travel |
| `dimensions` | TEXT / str | Size measurements |
| `notes` | TEXT / str | Optional additional info  |

## 2. Call Logs Schema (`call_logs` Table)
Captures backend operational metrics after the webhook dispatches the payload.

| Field Name | Type (DB / Pydantic) | Constraints / Description |
| :--- | :--- | :--- |
| `call_id` | TEXT / str | Primary Key. Sent by HappyRobot |
| `carrier_mc` | TEXT / str | Evaluated Motor Carrier identifier |
| `load_id` | TEXT / str | Foreign Key linking to `loads.load_id` |
| `final_rate` | NUMERIC / float | Agreed settlement price (if BOOKED) |
| `outcome` | TEXT / str | `BOOKED`, `REJECTED_RATE`, `VETTING_FAILED`, `HUNG_UP` |
| `sentiment` | TEXT / str | `positive`, `neutral`, `negative` |
| `duration_seconds`| INTEGER / int | Total telephone conversation length |
| `created_at` | TIMESTAMPTZ / datetime| Default: NOW() |