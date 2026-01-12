from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Project:
    name: str

@dataclass
class TimeEntry:
    project: Project
    start: datetime
    end: Optional[datetime] = None

    def is_running(self) -> bool:
        return self.end is None

    def duration_seconds(self) -> int:
        if self.is_running():
            raise ValueError("Time entry is still running")
        return int((self.end - self.start).total_seconds())
