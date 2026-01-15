import tkinter as tk
from tkinter import ttk, messagebox

from core.model import Project
from core.tracker import TimeTracker
from db.repository import TimeEntryRepository

def gui_main():
    repo = TimeEntryRepository()
    tracker = TimeTracker(repo)

    root = tk.Tk()
    root.title("Time Tracker")
    root.geometry("400x250")

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Project").pack(anchor="w")
    project_entry = ttk.Entry(frame)
    project_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Label").pack(anchor="w")
    label_entry = ttk.Entry(frame)
    label_entry.insert(0, "default")
    label_entry.pack(fill="x", pady=5)

    def on_start():
        name = project_entry.get().strip()
        label = label_entry.get().strip()

        if not name:
            messagebox.show_error("Error", "Project name is required")
            return

        try:
            project = Project(id=None, name=name, label=label)
            tracker.start(project)
            messagebox.showinfo("Started", f"Started tracking '{name}'")
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    def on_stop():
        try:
            entry = tracker.stop()
            messagebox.showinfo(
                "Stopped",
                f"Project: {entry.project.name}\n"
                f"Time spent: {entry.duration_seconds()} sec"
            )
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(frame, text="Start", command=on_start).pack(pady=10)
    ttk.Button(frame, text="Stop", command=on_stop).pack()

    root.mainloop()


if __name__ == "__main__":
    gui_main()
