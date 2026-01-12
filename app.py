from core.model import Project, TimeEntry
from core.tracker import TimeTracker

import time

tracker = TimeTracker()
project = Project("pks")

tracker.start(project)
time.sleep(2)
tracker.stop()

print(tracker.total_time_seconds(project))
