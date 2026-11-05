-- Roadmap v2: optional progress (0-100) and an optional link to a wiki page per item.
ALTER TABLE roadmap_items ADD COLUMN progress INTEGER CHECK (progress IS NULL OR progress BETWEEN 0 AND 100);
ALTER TABLE roadmap_items ADD COLUMN link TEXT NOT NULL DEFAULT '' CHECK (length(link) <= 200);
