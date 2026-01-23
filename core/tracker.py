from datetime import datetime
from typing import Optional, List

from core.model import Project, TimeEntry
from db.repository import TimeEntryRepository

class TimeTracker:

    def __init__(self, repo: TimeEntryRepository):
        self.repo = repo

    def start(self, project: Project) -> TimeEntry:
        if self.repo.get_active() is not None:
            raise RuntimeError("A time entry is already running")

        entry = TimeEntry(
            id=None,
            project=project,
            start=datetime.now()
        )

        self.repo.save_active(entry)
        return entry

    def stop(self) -> TimeEntry:
        active = self.repo.get_active()
        if active is None:
            raise RuntimeError("No active time entry")

        self.repo.stop_active(datetime.now())

        finished = self.repo.get_last_finished()
        return finished

    def delete(self, entry_id: int) -> bool:
        return self.repo.delete_entry(entry_id)

    def history(self):
        return self.repo.get_history()

    def summary(self, project_name=None, label_name=None):
        return self.repo.get_summary_sql(project_name, label_name)
    
    def get_active(self) -> TimeEntry | None:
        return self.repo.get_active()