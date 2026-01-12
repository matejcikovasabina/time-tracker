from datetime import datetime
from typing import List, Optional

from core.model import Project, TimeEntry


class TimeTracker:

    def __init__(self):
        self.entries: List[TimeEntry] = []
        self.active_entry: Optional[TimeEntry] = None

    def start(self, project: Project):
        if self.active_entry is not None:
            raise RuntimeError("A time entry is already running")

        entry = TimeEntry(
            project=project,
            start=datetime.now()
        )
        self.entries.append(entry)
        self.active_entry = entry

    def stop(self):
        if self.active_entry is None:
            raise RuntimeError("No active time entry")

        self.active_entry.end = datetime.now()
        self.active_entry = None

    def total_time_seconds(self, project: Project) -> int:
        total = 0
        for entry in self.entries:
            if entry.project.name == project.name and entry.end is not None:
                total += entry.duration_seconds()
        return total
