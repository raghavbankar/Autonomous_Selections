"""
Supabase Database Schema Setup
==============================

This file contains SQL statements to create all required tables in Supabase.

Follow these steps:
1. Go to your Supabase project: https://app.supabase.com
2. Navigate to SQL Editor
3. Create a new query
4. Copy and paste the SQL below
5. Execute the query

The script will create all tables with proper indexes and constraints.
"""

# ============================================================================
# SQL SETUP SCRIPT FOR SUPABASE
# ============================================================================

SQL_SETUP = """
-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. CANDIDATES TABLE
-- Stores candidate information
CREATE TABLE IF NOT EXISTS candidates (
    id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_candidates_created_at ON candidates(created_at);
CREATE INDEX idx_candidates_updated_at ON candidates(updated_at);


-- 2. INTERVIEW_ROUNDS TABLE
-- Stores interview round data and responses
CREATE TABLE IF NOT EXISTS interview_rounds (
    id BIGSERIAL PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    responses JSONB NOT NULL,
    scores JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interview_rounds_candidate_id ON interview_rounds(candidate_id);
CREATE INDEX idx_interview_rounds_round_number ON interview_rounds(round_number);
CREATE INDEX idx_interview_rounds_timestamp ON interview_rounds(timestamp);


-- 3. EVALUATIONS TABLE
-- Stores evaluation scores across dimensions
CREATE TABLE IF NOT EXISTS evaluations (
    id BIGSERIAL PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    technical_skills FLOAT CHECK (technical_skills >= 0 AND technical_skills <= 100),
    communication FLOAT CHECK (communication >= 0 AND communication <= 100),
    problem_solving FLOAT CHECK (problem_solving >= 0 AND problem_solving <= 100),
    cultural_fit FLOAT CHECK (cultural_fit >= 0 AND cultural_fit <= 100),
    authenticity FLOAT CHECK (authenticity >= 0 AND authenticity <= 100),
    final_score FLOAT CHECK (final_score >= 0 AND final_score <= 100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evaluations_candidate_id ON evaluations(candidate_id);
CREATE INDEX idx_evaluations_final_score ON evaluations(final_score);
CREATE INDEX idx_evaluations_timestamp ON evaluations(timestamp);


-- 4. AUTHENTICITY_CHECKS TABLE
-- Stores authenticity analysis results
CREATE TABLE IF NOT EXISTS authenticity_checks (
    id BIGSERIAL PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    is_authentic BOOLEAN NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    details JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_authenticity_checks_candidate_id ON authenticity_checks(candidate_id);
CREATE INDEX idx_authenticity_checks_is_authentic ON authenticity_checks(is_authentic);
CREATE INDEX idx_authenticity_checks_timestamp ON authenticity_checks(timestamp);


-- 5. SHORTLISTS TABLE
-- Stores shortlist snapshots
CREATE TABLE IF NOT EXISTS shortlists (
    id BIGSERIAL PRIMARY KEY,
    candidate_ids JSONB NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'completed')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shortlists_status ON shortlists(status);
CREATE INDEX idx_shortlists_timestamp ON shortlists(timestamp);


-- 6. HIRING_OUTCOMES TABLE
-- Stores final hiring decisions and feedback
CREATE TABLE IF NOT EXISTS hiring_outcomes (
    id BIGSERIAL PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    hired BOOLEAN NOT NULL,
    feedback TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hiring_outcomes_candidate_id ON hiring_outcomes(candidate_id);
CREATE INDEX idx_hiring_outcomes_hired ON hiring_outcomes(hired);
CREATE INDEX idx_hiring_outcomes_timestamp ON hiring_outcomes(timestamp);


-- 7. SYSTEM_STATS TABLE (Optional)
-- Stores aggregate statistics for system learning
CREATE TABLE IF NOT EXISTS system_stats (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_stats_metric_name ON system_stats(metric_name);
CREATE INDEX idx_system_stats_timestamp ON system_stats(timestamp);


-- Set up Row Level Security (Recommended)
-- You can customize these policies based on your authentication setup

-- Enable RLS on all tables
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE authenticity_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE hiring_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_stats ENABLE ROW LEVEL SECURITY;

-- Create basic RLS policies (allow all for now, customize as needed)
-- For production, implement proper user-based access control

CREATE POLICY "Allow all access" ON candidates FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON interview_rounds FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON evaluations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON authenticity_checks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON shortlists FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON hiring_outcomes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON system_stats FOR ALL USING (true) WITH CHECK (true);

-- Create views for common queries
CREATE VIEW candidate_scores AS
SELECT 
    c.id,
    c.data ->> 'name' as name,
    c.data ->> 'email' as email,
    e.technical_skills,
    e.communication,
    e.problem_solving,
    e.cultural_fit,
    e.authenticity,
    e.final_score,
    ac.is_authentic,
    ac.confidence_score,
    e.timestamp
FROM candidates c
LEFT JOIN evaluations e ON c.id = e.candidate_id
LEFT JOIN authenticity_checks ac ON c.id = ac.candidate_id;

CREATE VIEW hiring_summary AS
SELECT 
    COUNT(DISTINCT c.id) as total_candidates,
    COUNT(DISTINCT CASE WHEN ho.hired THEN ho.candidate_id END) as hired_count,
    ROUND(COUNT(DISTINCT CASE WHEN ho.hired THEN ho.candidate_id END)::numeric / COUNT(DISTINCT c.id) * 100, 2) as hiring_rate_percent,
    COUNT(DISTINCT CASE WHEN ac.is_authentic THEN ac.candidate_id END) as authentic_candidates
FROM candidates c
LEFT JOIN hiring_outcomes ho ON c.id = ho.candidate_id
LEFT JOIN authenticity_checks ac ON c.id = ac.candidate_id;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for candidates table
CREATE TRIGGER update_candidates_updated_at
BEFORE UPDATE ON candidates
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Verify tables were created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
"""


# ============================================================================
# SAMPLE QUERIES FOR ANALYTICS
# ============================================================================

SAMPLE_QUERIES = """
-- 1. Get candidates with final scores
SELECT 
    c.data ->> 'name' as name,
    e.final_score,
    e.timestamp
FROM candidates c
JOIN evaluations e ON c.id = e.candidate_id
ORDER BY e.final_score DESC;

-- 2. Get hiring success metrics
SELECT 
    COUNT(*) as total_processed,
    SUM(CASE WHEN ho.hired THEN 1 ELSE 0 END) as total_hired,
    ROUND(SUM(CASE WHEN ho.hired THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as hiring_rate
FROM candidates c
LEFT JOIN hiring_outcomes ho ON c.id = ho.candidate_id;

-- 3. Get candidates with authenticity issues
SELECT 
    c.data ->> 'name' as name,
    ac.is_authentic,
    ac.confidence_score,
    ac.details
FROM candidates c
JOIN authenticity_checks ac ON c.id = ac.candidate_id
WHERE ac.is_authentic = false
ORDER BY ac.confidence_score;

-- 4. Get interview performance by round
SELECT 
    ir.round_number,
    COUNT(*) as num_candidates,
    AVG((ir.scores ->> 'q1_score')::float) as avg_q1_score,
    AVG((ir.scores ->> 'q2_score')::float) as avg_q2_score,
    AVG((ir.scores ->> 'q3_score')::float) as avg_q3_score
FROM interview_rounds ir
GROUP BY ir.round_number
ORDER BY ir.round_number;

-- 5. Get top shortlisted candidates
SELECT 
    c.data ->> 'name' as name,
    c.data ->> 'email' as email,
    e.final_score,
    s.timestamp as shortlisted_at
FROM shortlists s, jsonb_array_elements_text(s.candidate_ids) as cid
JOIN candidates c ON c.id = cid
JOIN evaluations e ON c.id = e.candidate_id
WHERE s.status = 'active'
ORDER BY e.final_score DESC;

-- 6. Get evaluation dimension statistics
SELECT 
    ROUND(AVG(technical_skills), 2) as avg_technical_skills,
    ROUND(AVG(communication), 2) as avg_communication,
    ROUND(AVG(problem_solving), 2) as avg_problem_solving,
    ROUND(AVG(cultural_fit), 2) as avg_cultural_fit,
    ROUND(AVG(authenticity), 2) as avg_authenticity,
    ROUND(AVG(final_score), 2) as avg_final_score
FROM evaluations;

-- 7. Get candidates by seniority and score
SELECT 
    c.data ->> 'name' as name,
    c.data ->> 'seniority_level' as seniority,
    e.final_score
FROM candidates c
JOIN evaluations e ON c.id = e.candidate_id
WHERE (c.data ->> 'seniority_level') = 'senior'
ORDER BY e.final_score DESC;

-- 8. Get interview progression for a candidate
SELECT 
    ir.round_number,
    ir.responses,
    ir.scores,
    ir.timestamp
FROM interview_rounds ir
WHERE ir.candidate_id = 'candidate_id_here'
ORDER BY ir.round_number;
"""


# ============================================================================
# BACKUP & MAINTENANCE
# ============================================================================

MAINTENANCE_QUERIES = """
-- Backup candidates table
-- This should be run regularly (e.g., weekly)
CREATE TABLE candidates_backup AS SELECT * FROM candidates;

-- Clean up old data (keep last 1 year)
DELETE FROM interview_rounds 
WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 year';

DELETE FROM evaluations 
WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 year';

DELETE FROM authenticity_checks 
WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 year';

-- Analyze tables for query optimization
ANALYZE candidates;
ANALYZE interview_rounds;
ANALYZE evaluations;
ANALYZE authenticity_checks;
ANALYZE shortlists;
ANALYZE hiring_outcomes;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"""


if __name__ == "__main__":
    print("Supabase Database Schema Setup")
    print("="*60)
    print("\n1. Copy the SQL setup script below:")
    print("-"*60)
    print(SQL_SETUP)
    print("-"*60)
    print("\n2. Sample Analytics Queries:")
    print("-"*60)
    print(SAMPLE_QUERIES)
    print("-"*60)
    print("\n3. Maintenance Queries (optional):")
    print("-"*60)
    print(MAINTENANCE_QUERIES)
    print("-"*60)
    print("\nNext steps:")
    print("1. Go to https://app.supabase.com/project/[your-project-id]/sql/new")
    print("2. Paste the SQL setup script")
    print("3. Click 'Run'")
    print("4. Tables will be created automatically")
    print("\nFor Row Level Security:")
    print("- Edit RLS policies based on your authentication")
    print("- By default, all policies are set to allow all access")
    print("- Customize these for production use")
