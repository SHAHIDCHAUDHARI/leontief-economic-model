"""Read and save Leontief scenarios in SQLite."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3

from leontief import validate_inputs

DB_DIR = Path(__file__).resolve().parent / "db"
DB_PATH = DB_DIR / "leontief.sqlite3"
BASE_SCENARIO = 1


@contextmanager
def connect(path):
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            yield connection
    finally:
        connection.close()


def initialize(path=DB_PATH):
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8")
    sample = (DB_DIR / "sample.sql").read_text(encoding="utf-8")
    with connect(path) as connection:
        connection.executescript(f"BEGIN IMMEDIATE;\n{schema}\n{sample}\nCOMMIT;")


def list_scenarios(path=DB_PATH):
    with connect(path) as connection:
        return dict(connection.execute(
            "SELECT id, name FROM scenarios WHERE id != ? ORDER BY id DESC",
            (BASE_SCENARIO,),
        ))


def load_scenario(scenario_id, path=DB_PATH):
    with connect(path) as connection:
        sectors = [name for (name,) in connection.execute(
            "SELECT name FROM sectors WHERE scenario_id = ? ORDER BY position", (scenario_id,),
        )]
        if not sectors:
            raise ValueError("This scenario is no longer available.")
        demand = [amount for (amount,) in connection.execute(
            "SELECT amount FROM demands WHERE scenario_id = ? ORDER BY sector", (scenario_id,),
        )]
        inputs = [[0.0] * len(sectors) for _ in sectors]
        for supplier, producer, rate in connection.execute(
            "SELECT supplier, producer, rate FROM consumption_matrix WHERE scenario_id = ?",
            (scenario_id,),
        ):
            inputs[supplier][producer] = rate
    return sectors, inputs, demand


def save_scenario(name, sectors, inputs, demand, path=DB_PATH):
    name = name.strip()
    if not 1 <= len(name) <= 60:
        raise ValueError("Enter a scenario name of 1 to 60 characters.")
    if len(set(sectors)) != len(sectors):
        raise ValueError("Give each sector a different name.")
    validate_inputs(inputs, demand)

    with connect(path) as connection:
        scenario_id = connection.execute(
            "INSERT INTO scenarios (name) VALUES (?)", (name,),
        ).lastrowid
        connection.executemany(
            "INSERT INTO sectors VALUES (?, ?, ?)",
            [(scenario_id, position, sector) for position, sector in enumerate(sectors)],
        )
        connection.executemany(
            "INSERT INTO demands VALUES (?, ?, ?)",
            [(scenario_id, position, amount) for position, amount in enumerate(demand)],
        )
        connection.executemany(
            "INSERT INTO consumption_matrix VALUES (?, ?, ?, ?)",
            [(scenario_id, supplier, producer, rate)
             for supplier, row in enumerate(inputs)
             for producer, rate in enumerate(row)],
        )
    return scenario_id
