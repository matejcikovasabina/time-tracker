from collections import defaultdict
from typing import List
from core.model import TimeEntry

def summarize_by_project(entries: List[TimeEntry]) -> dict[str, int]:
    summary = defaultdict(int)

    for entry in entries:
        summary[entry.project.name] += entry.duration_seconds()

    return summary
