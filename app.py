from core.model import Project, TimeEntry
from core.tracker import TimeTracker

import argparse
import time

tracker = TimeTracker()
active_project = None

def main():
    parser = argparse.ArgumentParser(description = "Time Tracker CLI")

    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("project")

    end_parser = subparsers.add_parser("stop")

    args = parser.parse_args()

    global active_project
    
    if args.command == "start":
        active_project = Project(args.project)
        tracker.start(active_project)
        print(f"Started tracking project '{args.project}'")
    
    elif args.command == "stop":
        tracker.stop()
        seconds = tracker.total_time_seconds(active_project)

        print(f"Project: {active_project.name}")
        print(f"Time spend: {seconds}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

