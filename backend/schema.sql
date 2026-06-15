-- HappyRobot freight brokerage schema (PostgreSQL / Supabase)
-- Run this script in the Supabase SQL editor to provision persistence tables.

CREATE TABLE IF NOT EXISTS loads (
    load_id          TEXT PRIMARY KEY,
    origin           TEXT NOT NULL,
    destination      TEXT NOT NULL,
    pickup_datetime  TIMESTAMPTZ NOT NULL,
    delivery_datetime TIMESTAMPTZ NOT NULL,
    equipment_type   TEXT NOT NULL,
    loadboard_rate   NUMERIC NOT NULL,
    weight           NUMERIC NOT NULL,
    commodity_type   TEXT NOT NULL,
    num_of_pieces    INTEGER NOT NULL,
    miles            NUMERIC NOT NULL,
    dimensions       TEXT NOT NULL,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS call_logs (
    call_id          TEXT PRIMARY KEY,
    carrier_mc       TEXT NOT NULL,
    load_id          TEXT,
    final_rate       NUMERIC,
    outcome          TEXT NOT NULL,
    sentiment        TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT call_logs_load_id_fkey
        FOREIGN KEY (load_id)
        REFERENCES loads (load_id)
        ON DELETE SET NULL
);
