import tkinter as tk
from tkinter import ttk, messagebox

from core.model import Project
from core.tracker import TimeTracker
from db.repository import TimeEntryRepository

class TimeTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.repo = TimeEntryRepository()
        self.tracker = TimeTracker(self.repo)

        self.active_entry = None
        self.timer_running = False
        self.time_var = tk.StringVar(value="0.0 s")

        self.title("Time Tracker")
        self.geometry("250x300")

        self.frames = {}
        self._create_frames()
        self.show_frame("log")

        self.load_active()
        self.update_timer()

    def _create_frames(self):
        self.frames["log"] = LogFrame(self)
        self.frames["history"] = HistoryFrame(self)
        self.frames["summary"] = SummaryFrame(self)

        for frame in self.frames.values():
            frame.pack(fill="both", expand=True)
            frame.pack_forget()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()

        frame = self.frames[name]
        frame.pack(fill="both", expand=True)

        if name == "history":
            frame.refresh()


    def load_active(self):
        active = self.tracker.get_active()
        if active:
            self.active_entry = active
            self.timer_running = True
            self.frames["log"].fill_from_entry(active)

    def update_timer(self):
        if self.timer_running and self.active_entry:
            seconds = self.active_entry.elapsed_seconds()
            self.time_var.set(f"{seconds:.1f} s")
        else:
            self.time_var.set("0.0 s")

        self.after(100, self.update_timer)

class LogFrame(ttk.Frame):
    def __init__(self, app: TimeTrackerApp):
        super().__init__(app, padding=20)
        self.app = app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Project").grid(row=0, column=0, columnspan=2)
        self.project_entry = ttk.Entry(self)
        self.project_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(self, text="Label").grid(row=2, column=0, columnspan=2)
        self.label_entry = ttk.Entry(self)
        self.label_entry.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(self, text="Start", command=self.start)\
            .grid(row=4, column=0, pady=5)

        ttk.Button(self, text="Stop", command=self.stop)\
            .grid(row=4, column=1, pady=5)

        ttk.Label(self, textvariable=app.time_var)\
            .grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(self, text="History",
                   command=lambda: app.show_frame("history"))\
            .grid(row=6, column=0)

        ttk.Button(self, text="Summary",
                   command=lambda: app.show_frame("summary"))\
            .grid(row=6, column=1)

    def start(self):
        name = self.project_entry.get().strip()
        label = self.label_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Project name is required")
            return

        try:
            project = Project(id=None, name=name, label=label)
            self.app.active_entry = self.app.tracker.start(project)
            self.app.timer_running = True
            messagebox.showinfo("Started", f"Started tracking '{name}'")
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    def stop(self):
        try:
            entry = self.app.tracker.stop()
            self.app.active_entry = None
            self.app.timer_running = False
            self.clear()
            messagebox.showinfo(
                "Stopped",
                f"Project: {entry.project.name}\n"
                f"Time spent: {entry.duration_seconds()} s"
            )
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    def clear(self):
        self.project_entry.delete(0, tk.END)
        self.label_entry.delete(0, tk.END)

    def fill_from_entry(self, entry):
        self.project_entry.delete(0, tk.END)
        self.project_entry.insert(0, entry.project.name)

        self.label_entry.delete(0, tk.END)
        self.label_entry.insert(0, entry.project.label)

class HistoryFrame(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, padding=10)
        self.app = app

        ttk.Label(self, text="History").pack(anchor="w")

        columns = ("project", "label", "time")

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=8
        )

        self.tree.heading("project", text="Project")
        self.tree.heading("label", text="Label")
        self.tree.heading("time", text="Time")

        self.tree.column("project", width=75)
        self.tree.column("label", width=75)
        self.tree.column("time", width=80, anchor="e")

        self.tree.pack(fill="both", expand=True, pady=5)

        ttk.Button(
            self,
            text="Back",
            command=lambda: app.show_frame("log")
        ).pack()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        entries = self.app.tracker.repo.get_history()

        for entry in entries:
            self.tree.insert(
                "",
                "end",
                values=(
                    entry.project.name,
                    entry.project.label,
                    self._format_duration(entry.duration_seconds())
                )
            )

    @staticmethod
    def _format_duration(seconds: int) -> str:
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"


class SummaryFrame(ttk.Frame):
    def __init__(self, app: TimeTrackerApp):
        super().__init__(app, padding=20)
        self.app = app

        ttk.Label(self, text="Summary (TODO)").pack(pady=10)
        ttk.Button(self, text="Back",
                   command=lambda: app.show_frame("log")).pack()


def gui_main():
    app = TimeTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    gui_main()
