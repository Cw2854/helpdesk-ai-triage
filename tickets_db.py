"""
The ticket database
-------------------
Tickets are stored in SQLite: a small database that lives in one file (tickets.db)
and comes built into Python, so there's nothing to install.

Why a database instead of the Excel file?
  - A new ticket can always be saved, even while someone has the spreadsheet open in Excel
  - Two tickets arriving at the same moment can't overwrite each other
  - You can still download everything as Excel from the admin page

tickets.db contains people's names and messages, so it's listed in .gitignore
and never goes to GitHub.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tickets.db"

# Every column in the tickets table. The names match the fields used in triage.py.
FIELDS = [
    "ticket_id", "received", "from_name", "from_email", "subject", "message",
    "issue_summary", "category", "priority", "confidence", "needs_human_review",
    "review_reason", "ai_reason", "suggested_fix", "draft_reply", "triaged_at", "model",
    "expected_category", "category_correct", "expected_priority", "priority_correct",
    "source", "completed_at", "completed_by", "deleted_at", "deleted_by",
    # The facts the AI recorded, and its own priority guess (the rules set "priority")
    "people_affected", "can_work", "deadline", "security_risk", "ticket_type", "enough_info",
    "ai_priority", "priority_rule",
]

# The three lists in the admin queue, and which tickets belong in each.
# (Fixed text written here, never anything a user typed, so it's safe to put in the SQL.)
VIEWS = {
    "open": "deleted_at IS NULL AND completed_at IS NULL",
    "completed": "deleted_at IS NULL AND completed_at IS NOT NULL",
    "deleted": "deleted_at IS NOT NULL",
}


def connect():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row      # lets us read columns by name
    return connection


def create_table():
    """Create the tickets table the first time the app runs (does nothing after that)."""
    columns = ",\n            ".join(
        f"{field} REAL" if field == "confidence" else f"{field} TEXT"
        for field in FIELDS if field != "ticket_id"
    )
    with closing(connect()) as db, db:
        db.execute(f"""
            CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            {columns}
            )""")
        # If the database was made by an older version of the app, add any new columns
        existing = {row["name"] for row in db.execute("PRAGMA table_info(tickets)")}
        for field in FIELDS:
            if field not in existing:
                db.execute(f"ALTER TABLE tickets ADD COLUMN {field} TEXT")
        # Ticket numbers that were permanently deleted. Only the number is kept (nothing
        # personal), so the ticket isn't copied back in from Excel and the number isn't reused.
        db.execute("""
            CREATE TABLE IF NOT EXISTS purged_tickets (
            ticket_id TEXT PRIMARY KEY,
            purged_at TEXT,
            purged_by TEXT
            )""")


def add_ticket(ticket):
    """Save one ticket. Returns True if it was added, False if that ticket number already exists
    (or was permanently deleted, in which case it must stay deleted)."""
    # The ? placeholders mean the values are never mixed into the SQL itself,
    # which protects against SQL injection from whatever someone types in a ticket.
    sql = (f"INSERT OR IGNORE INTO tickets ({', '.join(FIELDS)}) "
           f"VALUES ({', '.join('?' for _ in FIELDS)})")
    with closing(connect()) as db, db:
        if db.execute("SELECT 1 FROM purged_tickets WHERE ticket_id = ?",
                      (ticket.get("ticket_id"),)).fetchone():
            return False
        cursor = db.execute(sql, [ticket.get(field) for field in FIELDS])
        return cursor.rowcount == 1


def next_ticket_id():
    """The next free ticket number, e.g. INC-1019 if the highest so far is INC-1018."""
    with closing(connect()) as db:
        ids = [row[0] for row in db.execute(
            "SELECT ticket_id FROM tickets UNION SELECT ticket_id FROM purged_tickets")]
    numbers = [int(i[4:]) for i in ids if i and i.startswith("INC-") and i[4:].isdigit()]
    return f"INC-{max(numbers, default=1000) + 1}"


def create_ticket(ticket):
    """Give a new ticket the next number and save it. Returns the ticket number."""
    for _ in range(5):      # if two tickets grab the same number at once, try the next one
        ticket["ticket_id"] = next_ticket_id()
        if add_ticket(ticket):
            return ticket["ticket_id"]
    raise RuntimeError("Couldn't save the ticket. Please try again.")


def tickets_in(view="open"):
    """The tickets in one list: "open", "completed" or "deleted"."""
    with closing(connect()) as db:
        return [dict(row) for row in db.execute(
            f"SELECT * FROM tickets WHERE {VIEWS[view]} ORDER BY id")]


def count_tickets(view="open"):
    with closing(connect()) as db:
        return db.execute(f"SELECT COUNT(*) FROM tickets WHERE {VIEWS[view]}").fetchone()[0]


def latest_row():
    """The internal number of the newest ticket (0 if there are none)."""
    with closing(connect()) as db:
        return db.execute("SELECT COALESCE(MAX(id), 0) FROM tickets").fetchone()[0]


def count_newer_than(row):
    """How many open tickets arrived after the given internal number."""
    with closing(connect()) as db:
        return db.execute(f"SELECT COUNT(*) FROM tickets WHERE id > ? AND {VIEWS['open']}",
                          (row,)).fetchone()[0]


def view_counts():
    """How many tickets are in each list, e.g. {"open": 18, "completed": 2, "deleted": 1}."""
    return {view: count_tickets(view) for view in VIEWS}


def _update(sql, values):
    """Run an UPDATE and say whether it changed a ticket."""
    with closing(connect()) as db, db:
        return db.execute(sql, values).rowcount == 1


# Nothing is ever wiped. Completing or deleting a ticket just records when and by whom,
# which means:
#  - it can always be undone (reopened or restored)
#  - there's a record of who did what, and when
#  - ticket numbers are never reused
#  - a deleted ticket isn't copied back in from the Excel results when the app restarts

def complete_ticket(ticket_id, by):
    return _update("UPDATE tickets SET completed_at = datetime('now', 'localtime'), completed_by = ? "
                   "WHERE ticket_id = ? AND completed_at IS NULL AND deleted_at IS NULL",
                   (by, ticket_id))


def reopen_ticket(ticket_id):
    return _update("UPDATE tickets SET completed_at = NULL, completed_by = NULL "
                   "WHERE ticket_id = ? AND completed_at IS NOT NULL AND deleted_at IS NULL",
                   (ticket_id,))


def delete_ticket(ticket_id, by):
    return _update("UPDATE tickets SET deleted_at = datetime('now', 'localtime'), deleted_by = ? "
                   "WHERE ticket_id = ? AND deleted_at IS NULL",
                   (by, ticket_id))


def restore_ticket(ticket_id):
    """Bring a deleted ticket back to the list it was in (Open or Completed)."""
    return _update("UPDATE tickets SET deleted_at = NULL, deleted_by = NULL "
                   "WHERE ticket_id = ? AND deleted_at IS NOT NULL",
                   (ticket_id,))


# Permanently deleting ("purging") removes the ticket and everything in it from the database.
# Only tickets already in the Deleted list can be purged, as a second layer of protection.

def _purge(db, ticket_ids, by):
    db.executemany(
        "INSERT OR IGNORE INTO purged_tickets (ticket_id, purged_at, purged_by) "
        "VALUES (?, datetime('now', 'localtime'), ?)",
        [(ticket_id, by) for ticket_id in ticket_ids])
    db.executemany("DELETE FROM tickets WHERE ticket_id = ? AND deleted_at IS NOT NULL",
                   [(ticket_id,) for ticket_id in ticket_ids])


def purge_ticket(ticket_id, by):
    """Permanently delete one ticket from the Deleted list. Returns True if it was removed."""
    with closing(connect()) as db, db:
        if not db.execute("SELECT 1 FROM tickets WHERE ticket_id = ? AND deleted_at IS NOT NULL",
                          (ticket_id,)).fetchone():
            return False
        _purge(db, [ticket_id], by)
    shrink()
    return True


def purge_deleted(ticket_ids, by):
    """Permanently delete these tickets, if they're still in the Deleted list.
    (Only the ones the admin saw on the confirmation page, never anything deleted since.)
    Returns how many tickets were removed."""
    wanted = set(ticket_ids)
    with closing(connect()) as db, db:
        ids = [row[0] for row in db.execute(
            f"SELECT ticket_id FROM tickets WHERE {VIEWS['deleted']}") if row[0] in wanted]
        _purge(db, ids, by)
    shrink()
    return len(ids)


def get_ticket(ticket_id):
    with closing(connect()) as db:
        row = db.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None


def shrink():
    """Give the freed space back, so tickets.db actually gets smaller after deleting."""
    with closing(connect()) as db:
        db.execute("VACUUM")
