-- Roadmap: items + a snapshot history for rollback.
CREATE TABLE IF NOT EXISTS roadmap_items (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT    NOT NULL CHECK (length(title) BETWEEN 1 AND 80),
  description  TEXT    NOT NULL DEFAULT '' CHECK (length(description) <= 280),
  status       TEXT    NOT NULL CHECK (status IN ('live','next','planned','idea')),
  category     TEXT    NOT NULL CHECK (category IN ('Mod','Map','Script Extender','Mod Manager','Wiki')),
  sort_order   INTEGER NOT NULL DEFAULT 0,
  version      TEXT    NOT NULL DEFAULT '' CHECK (length(version) <= 20),
  release_date TEXT    NOT NULL DEFAULT '' CHECK (length(release_date) <= 10),
  draft        INTEGER NOT NULL DEFAULT 0 CHECK (draft IN (0,1)),
  updated_at   TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_roadmap_items_order ON roadmap_items (status, sort_order);

CREATE TABLE IF NOT EXISTS roadmap_history (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  saved_at  TEXT NOT NULL,
  saved_by  TEXT NOT NULL,           -- Access email (or 'local-dev')
  action    TEXT NOT NULL,           -- e.g. 'create', 'update', 'delete', 'reorder', 'restore'
  summary   TEXT NOT NULL DEFAULT '',
  snapshot  TEXT NOT NULL            -- JSON array of all items AFTER the change
);
CREATE INDEX IF NOT EXISTS idx_roadmap_history_saved ON roadmap_history (id DESC);
