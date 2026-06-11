-- Lightweight schema migration used as the documented baseline for the project.
-- Runtime migration is executed by backend/migrate.py through SQLAlchemy metadata.

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    muscle_group VARCHAR NOT NULL,
    sub_muscle VARCHAR,
    category VARCHAR,
    equipment VARCHAR,
    description TEXT,
    images TEXT,
    gif_url VARCHAR,
    instructions TEXT,
    name_pl VARCHAR,
    instructions_pl TEXT,
    is_warmup INTEGER
);

CREATE INDEX IF NOT EXISTS ix_exercises_id ON exercises (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_exercises_name ON exercises (name);
CREATE INDEX IF NOT EXISTS ix_exercises_muscle_group ON exercises (muscle_group);
CREATE INDEX IF NOT EXISTS ix_exercises_category ON exercises (category);
CREATE INDEX IF NOT EXISTS ix_exercises_equipment ON exercises (equipment);
