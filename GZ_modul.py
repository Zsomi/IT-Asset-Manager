import logging
from datetime import date
from pathlib import Path
import sqlite3

logging.basicConfig(
    filename="asset_manager.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

GZ_DB_FILE = Path(__file__).with_name("asset_manager.db")
GZ_ASSET_TAG_PREFIX = "PC-"
GZ_STATUSES = ("Elérhető", "Használatban", "Javítás alatt", "Selejtezett")
GZ_COMPUTER_FIELDS = (
    "id", "asset_tag", "name", "manufacturer", "model", "serial_number",
    "processor", "ram", "storage", "operating_system", "purchase_date",
    "status", "notes",
)


def GZ_log_message(message: str, level: str = "info") -> None:
    if level == "error":
        logging.error(message)
    else:
        logging.info(message)


def GZ_today() -> str:
    return date.today().isoformat()


def GZ_open_connection(file_path: Path | None = None) -> sqlite3.Connection:
    if file_path is None:
        file_path = GZ_DB_FILE
    connection = sqlite3.connect(file_path)
    connection.execute("PRAGMA foreign_keys = ON")
    GZ_log_message(f"Adatbázis-kapcsolat megnyitva: {file_path}")
    return connection


def GZ_create_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS computers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            manufacturer TEXT,
            model TEXT,
            serial_number TEXT,
            processor TEXT,
            ram TEXT,
            storage TEXT,
            operating_system TEXT,
            purchase_date TEXT,
            status TEXT NOT NULL DEFAULT 'Elérhető',
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            email TEXT,
            phone TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            computer_id INTEGER NOT NULL REFERENCES computers(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            assigned_at TEXT NOT NULL,
            returned_at TEXT
        );

        CREATE TABLE IF NOT EXISTS disposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            computer_id INTEGER NOT NULL REFERENCES computers(id),
            disposal_date TEXT NOT NULL,
            reason TEXT,
            notes TEXT
        );
        """
    )
    connection.commit()


def GZ_next_asset_tag(connection: sqlite3.Connection) -> str:
    row = connection.execute("SELECT COUNT(*) FROM computers").fetchone()
    return f"{GZ_ASSET_TAG_PREFIX}{row[0] + 1:03d}"


def GZ_rows_to_dicts(rows: list, fields: tuple) -> list:
    return [dict(zip(fields, row)) for row in rows]


class GZDataManager:
    def __init__(self, connection: sqlite3.Connection = None):
        self.connection = connection
        GZ_create_tables(self.connection)

    def GZ_next_asset_tag(self) -> str:
        return GZ_next_asset_tag(self.connection)

    def GZ_add_computer(self, computer: dict) -> int:
        if not computer.get("asset_tag") or not computer.get("name"):
            raise ValueError("A leltári szám és a számítógép neve kötelező mező.")
        if computer.get("status") not in GZ_STATUSES:
            computer["status"] = "Elérhető"
        cursor = self.connection.execute(
            """
            INSERT INTO computers
                (asset_tag, name, manufacturer, model, serial_number,
                 processor, ram, storage, operating_system,
                 purchase_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                computer.get("asset_tag"),
                computer.get("name"),
                computer.get("manufacturer"),
                computer.get("model"),
                computer.get("serial_number"),
                computer.get("processor"),
                computer.get("ram"),
                computer.get("storage"),
                computer.get("operating_system"),
                computer.get("purchase_date"),
                computer.get("status"),
                computer.get("notes"),
            ),
        )
        self.connection.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("A beszúrás nem adott vissza azonosítót.")
        GZ_log_message(f"Számítógép hozzáadva: {computer['asset_tag']}")
        return cursor.lastrowid

    def GZ_list_computers(self, search: str = "", status: str = "") -> list:
        filters = []
        params = []
        if search.strip():
            filters.append("(asset_tag LIKE ? OR name LIKE ?)")
            pattern = f"%{search.strip()}%"
            params.extend([pattern, pattern])
        if status in GZ_STATUSES:
            filters.append("status = ?")
            params.append(status)
        where = ""
        if filters:
            where = " WHERE " + " AND ".join(filters)
        query = "SELECT * FROM computers" + where + " ORDER BY asset_tag"
        rows = self.connection.execute(query, params).fetchall()
        return GZ_rows_to_dicts(rows, GZ_COMPUTER_FIELDS)
