CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 60)
);

CREATE TABLE IF NOT EXISTS sectors (
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (scenario_id, position),
    UNIQUE (scenario_id, name)
);

CREATE TABLE IF NOT EXISTS demands (
    scenario_id INTEGER NOT NULL,
    sector INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    PRIMARY KEY (scenario_id, sector),
    FOREIGN KEY (scenario_id, sector) REFERENCES sectors(scenario_id, position)
);

CREATE TABLE IF NOT EXISTS consumption_matrix (
    scenario_id INTEGER NOT NULL,
    supplier INTEGER NOT NULL,
    producer INTEGER NOT NULL,
    rate REAL NOT NULL CHECK (rate >= 0),
    PRIMARY KEY (scenario_id, supplier, producer),
    FOREIGN KEY (scenario_id, supplier) REFERENCES sectors(scenario_id, position),
    FOREIGN KEY (scenario_id, producer) REFERENCES sectors(scenario_id, position)
);
