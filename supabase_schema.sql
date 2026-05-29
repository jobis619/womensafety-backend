-- ============================================
--  SafeHer — Supabase SQL Schema
--  Run this in Supabase SQL Editor
-- ============================================

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id            BIGSERIAL PRIMARY KEY,
    name          TEXT        NOT NULL,
    email         TEXT        UNIQUE NOT NULL,
    phone         TEXT,
    password_hash TEXT        NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- EMERGENCY CONTACTS TABLE
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT REFERENCES users(id) ON DELETE CASCADE,
    name         TEXT    NOT NULL,
    phone        TEXT    NOT NULL,
    relationship TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- INCIDENTS TABLE
CREATE TABLE IF NOT EXISTS incidents (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT REFERENCES users(id) ON DELETE SET NULL,
    incident_type TEXT    NOT NULL,
    description   TEXT    NOT NULL,
    location      TEXT,
    status        TEXT    DEFAULT 'pending' CHECK (status IN ('pending','in_review','resolved','urgent')),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- SOS ALERTS TABLE
CREATE TABLE IF NOT EXISTS sos_alerts (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT REFERENCES users(id) ON DELETE SET NULL,
    latitude   DOUBLE PRECISION,
    longitude  DOUBLE PRECISION,
    status     TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ADMINS TABLE (for future multi-admin support)
CREATE TABLE IF NOT EXISTS admins (
    id         BIGSERIAL PRIMARY KEY,
    username   TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default admin (username: admin, password: 123)
INSERT INTO admins (username, password)
VALUES ('admin', '123')
ON CONFLICT (username) DO NOTHING;

-- ============================================
--  Row Level Security (RLS) Policies
-- ============================================

-- Enable RLS
ALTER TABLE users              ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergency_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents          ENABLE ROW LEVEL SECURITY;
ALTER TABLE sos_alerts         ENABLE ROW LEVEL SECURITY;
ALTER TABLE admins             ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS (used by Django backend)
-- These policies allow the service role full access
CREATE POLICY "Service role full access - users"
    ON users FOR ALL USING (true);

CREATE POLICY "Service role full access - contacts"
    ON emergency_contacts FOR ALL USING (true);

CREATE POLICY "Service role full access - incidents"
    ON incidents FOR ALL USING (true);

CREATE POLICY "Service role full access - sos"
    ON sos_alerts FOR ALL USING (true);

CREATE POLICY "Service role full access - admins"
    ON admins FOR ALL USING (true);

-- ============================================
--  Indexes for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_incidents_user_id  ON incidents(user_id);
CREATE INDEX IF NOT EXISTS idx_contacts_user_id   ON emergency_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_sos_user_id        ON sos_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_incidents_status   ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_created  ON incidents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sos_created        ON sos_alerts(created_at DESC);
