-- =============================================================================
-- AI Factory v2 — Supabase Database Schema
-- =============================================================================
-- Run this script once in the Supabase SQL editor for your project before
-- the first AI Factory cycle executes.
--
-- Tables
--   af_cycles       — one row per orchestration cycle
--   af_problems     — detected improvement opportunities (FK → af_cycles)
--   af_hypotheses   — candidate solutions evaluated during a cycle (FK → af_cycles)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Cycles
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS af_cycles (
    cycle_id                    TEXT        PRIMARY KEY,
    repository                  TEXT        NOT NULL,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    problems_count              INTEGER     NOT NULL DEFAULT 0,
    hypotheses_count            INTEGER     NOT NULL DEFAULT 0,
    rejected                    BOOLEAN     NOT NULL DEFAULT false,
    rejection_reason            TEXT,
    pr_url                      TEXT,
    pr_number                   INTEGER,
    selected_hypothesis_id      TEXT,
    selected_hypothesis_title   TEXT,
    selected_score_composite    NUMERIC(5, 2)
);

COMMENT ON TABLE af_cycles IS
    'One row per AI Factory v2 orchestration cycle across all connected repositories.';

-- ---------------------------------------------------------------------------
-- Problems
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS af_problems (
    id              TEXT        PRIMARY KEY,
    cycle_id        TEXT        NOT NULL REFERENCES af_cycles (cycle_id) ON DELETE CASCADE,
    title           TEXT        NOT NULL,
    description     TEXT,
    category        TEXT,
    priority        TEXT,
    affected_files  TEXT[]      DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_af_problems_cycle_id ON af_problems (cycle_id);

COMMENT ON TABLE af_problems IS
    'Improvement opportunities detected by the Analyzer Agent during a cycle.';

-- ---------------------------------------------------------------------------
-- Hypotheses
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS af_hypotheses (
    id                      TEXT        PRIMARY KEY,
    cycle_id                TEXT        NOT NULL REFERENCES af_cycles (cycle_id) ON DELETE CASCADE,
    problem_id              TEXT        NOT NULL,
    title                   TEXT        NOT NULL,
    description             TEXT,
    approach                TEXT,
    implementation_plan     TEXT,
    status                  TEXT,
    score_composite         NUMERIC(5, 2),
    score_business_impact   NUMERIC(5, 2),
    score_technical_risk    NUMERIC(5, 2),
    score_complexity        NUMERIC(5, 2),
    score_maintainability   NUMERIC(5, 2),
    score_scalability       NUMERIC(5, 2),
    critic_feedback         TEXT
);

CREATE INDEX IF NOT EXISTS idx_af_hypotheses_cycle_id   ON af_hypotheses (cycle_id);
CREATE INDEX IF NOT EXISTS idx_af_hypotheses_problem_id ON af_hypotheses (problem_id);

COMMENT ON TABLE af_hypotheses IS
    'Candidate solutions generated and evaluated by the Generator, Evaluator and Critic agents.';

-- ---------------------------------------------------------------------------
-- Row-Level Security (recommended — enable after verifying everything works)
-- ---------------------------------------------------------------------------
-- ALTER TABLE af_cycles     ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE af_problems   ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE af_hypotheses ENABLE ROW LEVEL SECURITY;
--
-- Allow the service-role key full access (used by the GitHub Action):
-- CREATE POLICY "service role full access" ON af_cycles     FOR ALL USING (true);
-- CREATE POLICY "service role full access" ON af_problems   FOR ALL USING (true);
-- CREATE POLICY "service role full access" ON af_hypotheses FOR ALL USING (true);
