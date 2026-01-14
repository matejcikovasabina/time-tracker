import argparse

from core.model import Project
from core.tracker import TimeTracker
from db.repository import TimeEntryRepository


def main():
    repo = TimeEntryRepository()
    tracker = TimeTracker(repo)

    parser = argparse.ArgumentParser(description="Time Tracker CLI")
    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("project")
    start_parser.add_argument("--label", default="default")

    subparsers.add_parser("stop")

    history_parser = subparsers.add_parser("history")
    history_parser.add_argument("project", nargs="?")
    history_parser.add_argument("--today", action="store_true")

    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("project", nargs="?")
    summary_parser.add_argument("--today", action="store_true")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("id", type=int)

    args = parser.parse_args()

    try:
        if args.command == "start":
            project = Project(
                id=None,
                name=args.project,
                label=args.label
            )
            tracker.start(project)
            print(f"Started tracking project '{args.project}'")

        elif args.command == "stop":
            entry = tracker.stop()
            print(f"Project: {entry.project.name}")
            print(f"Time spent: {entry.duration_seconds()} sec")

        elif args.command == "history":
            rows = tracker.history(args.project, args.today)
            for id, project, start, end in rows:
                print(f"{id} | {project}: {start} - {end}")

        elif args.command == "summary":
            rows = tracker.summary(args.project, args.today)
            if not rows:
                print("No data.")
            for project, seconds in rows:
                print(f"{project}: {seconds} sec")

        elif args.command == "delete":
            if tracker.delete(args.id):
                print("Entry deleted.")
            else:
                print("No such entry.")

        else:
            parser.print_help()

    except RuntimeError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
