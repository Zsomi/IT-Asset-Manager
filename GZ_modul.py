import logging
from datetime import date, datetime
from pathlib import Path
import sqlite3
logging.basicConfig(
    filename="asset_manager.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
GZ_DB_FILE = Path(__file__).with_name("asset_manager.db")
ASSET_TAG_PREFIX = "PC-"
STATUSES = ("Elérhető", "Használatban", "Javítás alatt", "Selejtezett")
COMPUTER_FIELDS = (
    "id", "asset_tag", "name", "manufacturer", "model", "serial_number",
    "processor", "ram", "storage", "operating_system", "purchase_date",
    "status", "notes",
)
USER_FIELDS = ("id", "name", "department", "email", "phone", "notes")
ASSIGNMENT_FIELDS = ("id", "computer_id", "user_id", "assigned_at", "returned_at")
DISPOSAL_FIELDS = ("id", "computer_id", "disposal_date", "reason", "notes")
def GZ_validate_date(date_str):
    if date_str is None:
        return True
    try:
        datetime.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False
def GZ_log_message(message, level="info"):
    level = level.upper()
    if level == "DEBUG":
        logging.debug(message)
    elif level == "INFO":
        logging.info(message)
    elif level == "WARNING":
        logging.warning(message)
    elif level == "ERROR":
        logging.error(message)
    elif level == "CRITICAL":
        logging.critical(message)
    else:
        logging.info(message)
def GZ_today():
    return date.today().isoformat()
def open_connection(file_path=None):
    if file_path is None:
        file_path = GZ_DB_FILE
    connection = sqlite3.connect(file_path)
    connection.execute("PRAGMA foreign_keys = ON")
    GZ_log_message(f"Adatbázis-kapcsolat megnyitva: {file_path}")
    return connection
def create_tables(connection):
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
def next_asset_tag(connection):
    row = connection.execute("SELECT COUNT(*) FROM computers").fetchone()
    return f"{ASSET_TAG_PREFIX}{row[0] + 1:03d}"
def rows_to_dicts(rows, fields):
    return [dict(zip(fields, row)) for row in rows if len(row) == len(fields)]
class GZDataManager:
    def __init__(self, connection=None):
        self.connection = None
        if isinstance(connection, sqlite3.Connection):
            self.connection = connection
        elif connection is not None:
            file_path = Path(connection) if not isinstance(connection, Path) else connection
            self.connection = open_connection(file_path)
        if self.connection is None:
            self.connection = open_connection()
        create_tables(self.connection)
    def next_asset_tag(self):
        return next_asset_tag(self.connection)
    def get_computer_by_id(self, computer_id):
        row = self.connection.execute(
            "SELECT * FROM computers WHERE id = ?", (computer_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(zip(COMPUTER_FIELDS, row))
    def add_computer(self, computer):
        if not computer.get("asset_tag") or not computer.get("name"):
            raise ValueError("A leltári szám és a számítógép neve kötelező mező.")
        if computer.get("status") not in STATUSES:
            computer["status"] = "Elérhető"
        if computer.get("purchase_date") and not GZ_validate_date(computer.get("purchase_date")):
            raise ValueError(f"Érvénytelen dátum formátum: {computer.get('purchase_date')}. ISO formátum szükséges (YYYY-MM-DD).")
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
    def update_computer(self, computer_id, computer):
        if not computer.get("asset_tag") or not computer.get("name"):
            raise ValueError("A leltári szám és a név kötelező mező.")
        existing = self.get_computer_by_id(computer_id)
        if existing is None:
            return False
        if computer.get("status") not in STATUSES:
            computer["status"] = existing.get("status", "Elérhető")
        if computer.get("purchase_date") and not GZ_validate_date(computer.get("purchase_date")):
            raise ValueError(f"Érvénytelen dátum: {computer.get('purchase_date')}")
        self.connection.execute(
            """
            UPDATE computers
            SET asset_tag = ?, name = ?, manufacturer = ?, model = ?,
                serial_number = ?, processor = ?, ram = ?, storage = ?,
                operating_system = ?, purchase_date = ?, status = ?, notes = ?
            WHERE id = ?
            """,
            (
                computer.get("asset_tag", existing["asset_tag"]),
                computer.get("name", existing["name"]),
                computer.get("manufacturer", existing["manufacturer"]),
                computer.get("model", existing["model"]),
                computer.get("serial_number", existing["serial_number"]),
                computer.get("processor", existing["processor"]),
                computer.get("ram", existing["ram"]),
                computer.get("storage", existing["storage"]),
                computer.get("operating_system", existing["operating_system"]),
                computer.get("purchase_date", existing["purchase_date"]),
                computer.get("status", existing["status"]),
                computer.get("notes", existing["notes"]),
                computer_id,
            ),
        )
        self.connection.commit()
        GZ_log_message(f"Számítógép frissítve: {computer.get('asset_tag', existing['asset_tag'])}")
        return True
    def list_computers(self, search="", status=""):
        filters = []
        params = []
        if search.strip():
            filters.append("(asset_tag LIKE ? OR name LIKE ?)")
            params.extend([f"%{search.strip()}%", f"%{search.strip()}%"])
        if status in STATUSES:
            filters.append("status = ?")
            params.append(status)
        where = " WHERE " + " AND ".join(filters) if filters else ""
        query = f"SELECT * FROM computers{where} ORDER BY id"
        rows = self.connection.execute(query, params).fetchall()
        return rows_to_dicts(rows, COMPUTER_FIELDS)
    def add_user(self, user):
        if not user.get("name"):
            raise ValueError("A felhasználó neve kötelező mező.")
        cursor = self.connection.execute(
            """
            INSERT INTO users (name, department, email, phone, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user.get("name"),
                user.get("department"),
                user.get("email"),
                user.get("phone"),
                user.get("notes"),
            ),
        )
        self.connection.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("A felhasználó beszúrása nem adott vissza azonosítót.")
        GZ_log_message(f"Felhasználó hozzáadva: {user['name']}")
        return cursor.lastrowid
    def list_users(self, search="", department=""):
        filters = []
        params = []
        if search.strip():
            filters.append("(name LIKE ? OR email LIKE ?)")
            params.extend([f"%{search.strip()}%", f"%{search.strip()}%"])
        if department.strip():
            filters.append("department = ?")
            params.append(department)
        where = " WHERE " + " AND ".join(filters) if filters else ""
        query = f"SELECT * FROM users{where} ORDER BY name"
        rows = self.connection.execute(query, params).fetchall()
        return rows_to_dicts(rows, USER_FIELDS)
    def get_user_by_id(self, user_id):
        row = self.connection.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(zip(USER_FIELDS, row))
    def update_user(self, user_id, user):
        if not user.get("name"):
            raise ValueError("A felhasználó neve kötelező mező.")
        existing = self.get_user_by_id(user_id)
        if existing is None:
            return False
        self.connection.execute(
            """
            UPDATE users
            SET name = ?, department = ?, email = ?, phone = ?, notes = ?
            WHERE id = ?
            """,
            (
                user.get("name", existing["name"]),
                user.get("department", existing["department"]),
                user.get("email", existing["email"]),
                user.get("phone", existing["phone"]),
                user.get("notes", existing["notes"]),
                user_id,
            ),
        )
        self.connection.commit()
        GZ_log_message(f"Felhasználó frissítve: {user.get('name', existing['name'])}")
        return True
    def delete_user(self, user_id):
        active_assignments = self.connection.execute(
            "SELECT COUNT(*) FROM assignments WHERE user_id = ? AND returned_at IS NULL",
            (user_id,)
        ).fetchone()[0]
        if active_assignments > 0:
            raise ValueError("A felhasználónak van aktív kiadása, nem törölhető.")
        cursor = self.connection.execute(
            "DELETE FROM users WHERE id = ?", (user_id,)
        )
        self.connection.commit()
        if cursor.rowcount == 0:
            return False
        GZ_log_message(f"Felhasználó törölve: ID={user_id}")
        return True
    def assign_computer(self, computer_id, user_id, assigned_at=None):
        if assigned_at is None:
            assigned_at = GZ_today()
        if not GZ_validate_date(assigned_at):
            raise ValueError(f"Érvénytelen dátum: {assigned_at}")
        computer = self.get_computer_by_id(computer_id)
        if computer is None:
            raise ValueError(f"Számítógép nem található: ID={computer_id}")
        user = self.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"Felhasználó nem található: ID={user_id}")
        if computer["status"] != "Elérhető":
            raise ValueError(f"Csak elérhető gép adható ki: {computer['asset_tag']} (státusz: {computer['status']})")
        cursor = self.connection.execute(
            """
            INSERT INTO assignments (computer_id, user_id, assigned_at)
            VALUES (?, ?, ?)
            """,
            (computer_id, user_id, assigned_at),
        )
        self.connection.execute(
            "UPDATE computers SET status = ? WHERE id = ?",
            ("Használatban", computer_id),
        )
        self.connection.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("A kiadás rögzítése nem sikerült.")
        GZ_log_message(f"Számítógép kiadva: {computer['asset_tag']} -> {user['name']}")
        return cursor.lastrowid
    
    def assign_computer_by_name(self, computer_id, user_name, assigned_at=None):
        if assigned_at is None:
            assigned_at = GZ_today()
        if not GZ_validate_date(assigned_at):
            raise ValueError(f"Érvénytelen dátum: {assigned_at}")
        
        computer = self.get_computer_by_id(computer_id)
        if computer is None:
            raise ValueError(f"Számítógép nem található: ID={computer_id}")
        if computer["status"] != "Elérhető":
            raise ValueError(f"Csak elérhető gép adható ki: {computer['asset_tag']} (státusz: {computer['status']})")
        
        user = self.connection.execute(
            "SELECT * FROM users WHERE name = ?", (user_name.strip(),)
        ).fetchone()
        
        if user is None:
            cursor = self.connection.execute(
                "INSERT INTO users (name) VALUES (?)", (user_name.strip(),)
            )
            self.connection.commit()
            user_id = cursor.lastrowid
            GZ_log_message(f"Felhasználó automatikusan létrehozva: {user_name.strip()}")
        else:
            user_id = user[0]
        
        cursor = self.connection.execute(
            """
            INSERT INTO assignments (computer_id, user_id, assigned_at)
            VALUES (?, ?, ?)
            """,
            (computer_id, user_id, assigned_at),
        )
        self.connection.execute(
            "UPDATE computers SET status = ? WHERE id = ?",
            ("Használatban", computer_id),
        )
        self.connection.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("A kiadás rögzítése nem sikerült.")
        GZ_log_message(f"Számítógép kiadva: {computer['asset_tag']} -> {user_name.strip()}")
        return cursor.lastrowid
    def return_computer(self, assignment_id, returned_at=None):
        if returned_at is None:
            returned_at = GZ_today()
        if not GZ_validate_date(returned_at):
            raise ValueError(f"Érvénytelen dátum: {returned_at}")
        assignment = self.get_assignment_by_id(assignment_id)
        if assignment is None:
            return False
        if assignment["returned_at"] is not None:
            raise ValueError(f"Ez a kiadás már le van zárva (visszavéve: {assignment['returned_at']})")
        self.connection.execute(
            """
            UPDATE assignments SET returned_at = ? WHERE id = ?
            """,
            (returned_at, assignment_id),
        )
        self.connection.execute(
            "UPDATE computers SET status = ? WHERE id = ?",
            ("Elérhető", assignment["computer_id"]),
        )
        self.connection.commit()
        GZ_log_message(f"Számítógép visszavéve: kiadás ID={assignment_id}")
        return True
    def list_assignments(self, computer_id=None, user_id=None, active_only=False):
        filters = []
        params = []
        if computer_id is not None:
            filters.append("computer_id = ?")
            params.append(computer_id)
        if user_id is not None:
            filters.append("user_id = ?")
            params.append(user_id)
        if active_only:
            filters.append("returned_at IS NULL")
        where = " WHERE " + " AND ".join(filters) if filters else ""
        query = f"SELECT * FROM assignments{where} ORDER BY assigned_at DESC"
        rows = self.connection.execute(query, params).fetchall()
        return rows_to_dicts(rows, ASSIGNMENT_FIELDS)
    def get_assignment_by_id(self, assignment_id):
        row = self.connection.execute(
            "SELECT * FROM assignments WHERE id = ?", (assignment_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(zip(ASSIGNMENT_FIELDS, row))
    def add_disposal(self, computer_id, disposal_date=None, reason="", notes=""):
        if disposal_date is None:
            disposal_date = GZ_today()
        if not GZ_validate_date(disposal_date):
            raise ValueError(f"Érvénytelen dátum: {disposal_date}")
        computer = self.get_computer_by_id(computer_id)
        if computer is None:
            raise ValueError(f"Számítógép nem található: ID={computer_id}")
        if computer["status"] != "Elérhető":
            raise ValueError(f"Csak elérhető gép selejtezhető: {computer['asset_tag']} (státusz: {computer['status']})")
        cursor = self.connection.execute(
            """
            INSERT INTO disposals (computer_id, disposal_date, reason, notes)
            VALUES (?, ?, ?, ?)
            """,
            (computer_id, disposal_date, reason, notes),
        )
        self.connection.execute(
            "UPDATE computers SET status = ? WHERE id = ?",
            ("Selejtezett", computer_id),
        )
        self.connection.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("A selejtezés rögzítése nem sikerült.")
        GZ_log_message(f"Számítógép selejtezve: {computer['asset_tag']} (ok: {reason})")
        return cursor.lastrowid
    def list_disposals(self, computer_id=None, from_date=None, to_date=None):
        filters = []
        params = []
        if computer_id is not None:
            filters.append("computer_id = ?")
            params.append(computer_id)
        if from_date is not None and GZ_validate_date(from_date):
            filters.append("disposal_date >= ?")
            params.append(from_date)
        if to_date is not None and GZ_validate_date(to_date):
            filters.append("disposal_date <= ?")
            params.append(to_date)
        where = " WHERE " + " AND ".join(filters) if filters else ""
        query = f"SELECT * FROM disposals{where} ORDER BY disposal_date DESC"
        rows = self.connection.execute(query, params).fetchall()
        return rows_to_dicts(rows, DISPOSAL_FIELDS)
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            GZ_log_message("Adatbázis-kapcsolat bezárva")
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
