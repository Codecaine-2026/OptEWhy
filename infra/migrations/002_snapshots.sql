ALTER TABLE fcm_edges ADD COLUMN IF NOT EXISTS subsystem TEXT NOT NULL DEFAULT 'general';

CREATE TABLE IF NOT EXISTS fcm_snapshots (
  id TEXT PRIMARY KEY,
  terminal_id TEXT NOT NULL REFERENCES terminals(id),
  captured_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS fcm_snapshot_values (
  snapshot_id TEXT NOT NULL REFERENCES fcm_snapshots(id) ON DELETE CASCADE,
  node_id TEXT NOT NULL REFERENCES fcm_nodes(id),
  value DOUBLE PRECISION NOT NULL CHECK (value >= -1 AND value <= 1),
  PRIMARY KEY (snapshot_id, node_id)
);
