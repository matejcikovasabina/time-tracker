import sqlite3
from datetime import datetime
from typing import Optional

from core.model import Project, TimeEntry

DB_PATH = "tracker.db"


class TimeEntryRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT
            )
        """)
        self.conn.commit()

    def save_active(self, entry: TimeEntry):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO time_entries (project, start, end)
            VALUES (?, ?, NULL)
        """, (entry.project.name, entry.start.isoformat()))
        self.conn.commit()

    def get_active(self) -> Optional[TimeEntry]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT project, start
            FROM time_entries
            WHERE end IS NULL
            ORDER BY id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()

        if row is None:
            return None

        project_name, start_str = row
        return TimeEntry(
            project=Project(project_name),
            start=datetime.fromisoformat(start_str)
        )

    def stop_active(self, end_time: datetime):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE time_entries
            SET end = ?
            WHERE end IS NULL
        """, (end_time.isoformat(),))
        self.conn.commit()

    def get_history(self, project=None, today=False):
        cursor = self.conn.cursor()
        query = """
            SELECT id, project, start, end 
            FROM time_entries
            WHERE end IS NOT NULL
        """

        params = []

        if project:
            query += " AND project = ?"
            params.append(project)
        
        if today:
            query += " AND date(start) = date('now')"

        cursor.execute(query, params)
        return cursor.fetchall()

    def get_summary_sql(self, project=None, today=False):
        cursor = self.conn.cursor()

        query = """
            SELECT
                project,
                SUM(strftime('%s', end) - strftime('%s', start)) AS total_seconds
            FROM time_entries
            WHERE end IS NOT NULL
        """
        params = []

        if project:
            query += " AND project = ?"
            params.append(project)

        if today:
            query += " AND date(start) = date('now')"

        query += " GROUP BY project"

        cursor.execute(query, params)
        return cursor.fetchall()

    def delete_entry(self, entry_id: id):
        cursor = self.conn.cursor()

        cursor.execute(
                "DELETE FROM time_entries WHERE ID = ?",
                (entry_id,)
        )
        self.conn.commit()

        return cursor.rowcount > 0