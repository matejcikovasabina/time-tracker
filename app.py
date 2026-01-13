from core.model import Project, TimeEntry
from core.tracker import TimeTracker
from db.repository import TimeEntryRepository
import argparse
from datetime import datetime

repo = TimeEntryRepository()
tracker = TimeTracker()
active_project = None

def main():
    parser = argparse.ArgumentParser(description = "Time Tracker CLI")

    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("project")

    end_parser = subparsers.add_parser("stop")

    history_parser = subparsers.add_parser("history")

    summary_parser = subparsers.add_parser("summary")

    summary_parser.add_argument(
        "project",
        nargs="?",
        help="Project name"
    )

    summary_parser.add_argument(
        "--today",
        action="store_true",
        help="Only today's entries"
)

    args = parser.parse_args()

    global active_project
    
    if args.command == "start":
        active_project = Project(args.project)
        tracker.start(active_project)

        active = tracker.active_entry
        repo.save_active(active)

        print(f"Started tracking project '{args.project}'")
    
    elif args.command == "stop":
        active = repo.get_active()
        if active is None:
            print("No active time entry")
            return
        
        tracker.active_entry = active
        tracker.stop()

        repo.stop_active(active.end)
        seconds = active.duration_seconds()

        print(f"Project: {active.project.name}")
        print(f"Time spend: {seconds}")

    elif args.command == "history":
        rows = repo.get_history()
        for project, start, end in rows:
            print(f"{project}: start {start} - end {end}")

    elif args.command == "summary":
        rows = repo.get_summary_sql(
            project=args.project,
            today=args.today
        )

        if not rows:
            print("No data for given filter.")
            return

        for project, seconds in rows:
            print(f"{project}: {seconds} sec")


    else:
        parser.print_help()

if __name__ == "__main__":
    main()

