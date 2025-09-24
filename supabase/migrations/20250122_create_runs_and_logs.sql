-- Migration: Create runs and run_logs tables for automation logging
-- Task T2: Đồng bộ log backend ↔ web
-- Created: 2025-01-22

-- Table: runs
-- Quản lý các phiên chạy automation
CREATE TABLE IF NOT EXISTS runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMPTZ DEFAULT NOW(),
  stopped_at TIMESTAMPTZ,
  status TEXT CHECK (status IN ('running', 'stopped', 'failed', 'completed')) DEFAULT 'running',
  pair_count INTEGER DEFAULT 0,
  device_count INTEGER DEFAULT 0,
  created_by TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: run_logs
-- Lưu trữ log chi tiết cho từng run
CREATE TABLE IF NOT EXISTS run_logs (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
  ts TIMESTAMPTZ DEFAULT NOW(),
  level TEXT CHECK (level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'SUCCESS')) DEFAULT 'INFO',
  pair_id TEXT,
  device_a TEXT,
  device_b TEXT,
  action TEXT,
  message TEXT NOT NULL,
  meta JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_run_logs_run_id_ts ON run_logs(run_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_run_logs_level ON run_logs(level);
CREATE INDEX IF NOT EXISTS idx_run_logs_pair_id ON run_logs(pair_id);
CREATE INDEX IF NOT EXISTS idx_run_logs_action ON run_logs(action);

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger: Auto update updated_at for runs table
DROP TRIGGER IF EXISTS update_runs_updated_at ON runs;
CREATE TRIGGER update_runs_updated_at
    BEFORE UPDATE ON runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) policies
ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE run_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users on runs"
  ON runs
  FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow all operations for authenticated users on run_logs"
  ON run_logs
  FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Policy: Allow read access for anonymous users (for public dashboards)
CREATE POLICY "Allow read access for anonymous users on runs"
  ON runs
  FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Allow read access for anonymous users on run_logs"
  ON run_logs
  FOR SELECT
  TO anon
  USING (true);

-- Grant permissions
GRANT ALL PRIVILEGES ON runs TO authenticated;
GRANT ALL PRIVILEGES ON run_logs TO authenticated;
GRANT SELECT ON runs TO anon;
GRANT SELECT ON run_logs TO anon;
GRANT USAGE, SELECT ON SEQUENCE run_logs_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE run_logs_id_seq TO anon;

-- Sample data for testing (optional)
-- INSERT INTO runs (id, status, pair_count, device_count, created_by) 
-- VALUES 
--   ('550e8400-e29b-41d4-a716-446655440000', 'completed', 2, 4, 'test_user'),
--   ('550e8400-e29b-41d4-a716-446655440001', 'running', 1, 2, 'test_user');

-- INSERT INTO run_logs (run_id, level, pair_id, device_a, device_b, action, message)
-- VALUES 
--   ('550e8400-e29b-41d4-a716-446655440000', 'INFO', 'pair_1_2', '192.168.1.1', '192.168.1.2', 'START', 'Starting automation for pair'),
--   ('550e8400-e29b-41d4-a716-446655440000', 'SUCCESS', 'pair_1_2', '192.168.1.1', '192.168.1.2', 'COMPLETE', 'Automation completed successfully');

-- Comments
COMMENT ON TABLE runs IS 'Automation run sessions';
COMMENT ON TABLE run_logs IS 'Detailed logs for each automation run';
COMMENT ON COLUMN runs.status IS 'Current status of the run: running, stopped, failed, completed';
COMMENT ON COLUMN run_logs.level IS 'Log level: DEBUG, INFO, WARN, ERROR, SUCCESS';
COMMENT ON COLUMN run_logs.action IS 'Action being performed: START, STOP, PAIR_PROCESS, DEVICE_CONNECT, etc.';
COMMENT ON COLUMN run_logs.meta IS 'Additional metadata in JSON format';