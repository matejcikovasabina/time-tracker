import sqlite3
from datetime import datetime
from typing import Optional

from core.model import Project, TimeEntry, ProjectSummary

DB_PATH = "tracker.db"

class TimeEntryRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                label_id INTEGER NOT NULL,
                FOREIGN KEY(label_id) REFERENCES labels(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                start TEXT NOT NULL,
                end TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
        """)

        self.conn.commit()

    def save_active(self, entry: TimeEntry):
        cursor = self.conn.cursor()

        project_id = self.get_or_create_project(
            entry.project.name,
            entry.project.label
        )

        cursor.execute("""
            INSERT INTO time_entries (project_id, start, end)
            VALUES (?, ?, NULL)
        """, (
            project_id,
            entry.start.isoformat()
        ))

        self.conn.commit()

    def get_active(self) -> Optional[TimeEntry]:
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                t.id,
                p.id,
                p.name,
                l.name,
                t.start
            FROM time_entries t
            JOIN projects p ON t.project_id = p.id
            JOIN labels l ON p.label_id = l.id
            WHERE t.end IS NULL
            ORDER BY t.id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        if row is None:
            return None

        entry_id, project_id, project_name, label_name, start = row

        return TimeEntry(
            id=entry_id,
            project=Project(
                id=project_id,
                name=project_name,
                label=label_name
            ),
            start=datetime.fromisoformat(start)
        )

    def get_last_finished(self) -> TimeEntry:
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                t.id,
                p.id,
                p.name,
                l.name,
                t.start,
                t.end
            FROM time_entries t
            JOIN projects p ON t.project_id = p.id
            JOIN labels l ON p.label_id = l.id
            ORDER BY t.id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        entry_id, project_id, project_name, label_name, start, end = row

        return TimeEntry(
            id=entry_id,
            project=Project(
                id=project_id,
                name=project_name,
                label=label_name
            ),
            start=datetime.fromisoformat(start),
            end=datetime.fromisoformat(end)
        )

    def stop_active(self, end_time: datetime):
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE time_entries
            SET end = ?
            WHERE id = (
                SELECT id FROM time_entries
                WHERE end IS NULL
                ORDER BY id DESC
                LIMIT 1
            )
        """, (end_time.isoformat(),))

        self.conn.commit()

    def get_history(self) -> list[TimeEntry]:
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                t.id,
                p.id,
                p.name,
                l.name,
                t.start,
                t.end
            FROM time_entries t
            JOIN projects p ON t.project_id = p.id
            JOIN labels l ON p.label_id = l.id
            WHERE t.end IS NOT NULL
            ORDER BY t.start DESC
        """)

        entries = []

        for row in cursor.fetchall():
            (
                time_id,
                project_id,
                project_name,
                label_name,
                start,
                end
            ) = row

            project = Project(
                id=project_id,
                name=project_name,
                label=label_name
            )

            entry = TimeEntry(
                id=time_id,
                project=project,
                start=datetime.fromisoformat(start),
                end=datetime.fromisoformat(end)
            )

            entries.append(entry)

        return entries


    def get_summary_sql(
        self,
        project_name: Optional[str] = None,
        label_name: Optional[str] = None
    ) -> ProjectSummary:

        cursor = self.conn.cursor()

        query = """
            SELECT
                p.name,
                l.name,
                SUM(strftime('%s', t.end) - strftime('%s', t.start)) AS total_seconds
            FROM time_entries t
            JOIN projects p ON t.project_id = p.id
            JOIN labels l ON p.label_id = l.id
            WHERE t.end IS NOT NULL
        """

        params = []

        if project_name:
            query += " AND p.name = ?"
            params.append(project_name)

        if label_name:
            query += " AND l.name = ?"
            params.append(label_name)

        query += " GROUP BY p.id, p.name, l.name"
        query += " ORDER BY total_seconds DESC"

        cursor.execute(query, params)

        results = []
        for project, label, total_seconds in cursor.fetchall():
            results.append(
                ProjectSummary(
                    project_name=project,
                    label_name=label,
                    total_seconds=int(total_seconds)
                )
            )

        return results


    def delete_entry(self, entry_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM time_entries WHERE id = ?",
            (entry_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_or_create_label(self, name: str) -> int:
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM labels WHERE name = ?", 
                (name,)
        )
        row = cursor.fetchone()
        if row:
            return row[0]

        cursor.execute(
            "INSERT INTO labels (name) VALUES (?)",
            (name,)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_or_create_project(self, name: str, label_name: str) -> int:
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM projects WHERE name = ?", 
                (name,)
        )
        row = cursor.fetchone()
        if row:
            return row[0]

        label_id = self.get_or_create_label(label_name)

        cursor.execute(
            "INSERT INTO projects (name, label_id) VALUES (?, ?)",
            (name, label_id)
        )
        self.conn.commit()
        return cursor.lastrowid

