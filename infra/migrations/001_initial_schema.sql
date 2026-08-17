CREATE TABLE IF NOT EXISTS terminals (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  timezone TEXT NOT NULL DEFAULT 'Asia/Seoul'
);

CREATE TABLE IF NOT EXISTS fcm_nodes (
  id TEXT PRIMARY KEY,
  terminal_id TEXT NOT NULL REFERENCES terminals(id),
  label TEXT NOT NULL,
  node_type TEXT NOT NULL,
  subsystem TEXT NOT NULL,
  entity_id TEXT
);

CREATE TABLE IF NOT EXISTS fcm_edges (
  id TEXT PRIMARY KEY,
  terminal_id TEXT NOT NULL REFERENCES terminals(id),
  source_node_id TEXT NOT NULL REFERENCES fcm_nodes(id),
  target_node_id TEXT NOT NULL REFERENCES fcm_nodes(id),
  base_weight DOUBLE PRECISION NOT NULL CHECK (base_weight >= -1 AND base_weight <= 1),
  polarity TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (confidence >= 0 AND confidence <= 1)
);

CREATE TABLE IF NOT EXISTS analysis_audit_log (
  id TEXT PRIMARY KEY,
  terminal_id TEXT NOT NULL,
  request_text TEXT NOT NULL,
  snapshot_id TEXT NOT NULL,
  fcm_model_version TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

