import tkinter as tk
from tkinter import ttk, messagebox

from core.model import Project
from core.tracker import TimeTracker
from db.repository import TimeEntryRepository

class TimeTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        style = ttk.Style(self)
        style.theme_use("default")

        style.configure(
            "App.TFrame",
            background="#edcedd"
        )

        style.configure(
            "App.TLabel",
            background="#edcedd",
            foreground="black"
        )

        style.configure(
            "App.TButton",
            background="white",
            foreground="black",
            padding=6
        )

        style.map(
            "App.TButton",
            background=[("active", "#de9bbb")]
        )

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
        self.frames["overview"] = OverviewFrame(self)

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
        super().__init__(app, padding=20,style="App.TFrame")
        self.app = app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Project", style="App.TLabel").grid(row=0, column=0, columnspan=2)
        self.project_entry = ttk.Entry(self)
        self.project_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(self, text="Label", style="App.TLabel").grid(row=2, column=0, columnspan=2)
        self.label_entry = ttk.Entry(self)
        self.label_entry.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(self, text="Start", command=self.start, style="App.TButton")\
            .grid(row=4, column=0, pady=5)

        ttk.Button(self, text="Stop", command=self.stop, style="App.TButton")\
            .grid(row=4, column=1, pady=5)

        ttk.Label(self, textvariable=app.time_var, style="App.TLabel")\
            .grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(self, text="History",
                   command=lambda: app.show_frame("history"), style="App.TButton")\
            .grid(row=6, column=0)

        ttk.Button(self, text="Summary",
                   command=lambda: app.show_frame("summary"), style="App.TButton")\
            .grid(row=6, column=1)
        
        ttk.Button(self, text="Overview", command=lambda: app.show_frame("overview"),style="App.TButton")\
            .grid(row=7)

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
        super().__init__(app, padding=10, style="App.TFrame")
        self.app = app

        ttk.Label(self, text="History", style="App.TLabel").pack(pady=10)

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
            command=lambda: app.show_frame("log"), style="App.TButton"
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
        super().__init__(app, padding=20, style="App.TFrame")
        self.app = app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Summary", style="App.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        ttk.Label(self, text="Project", style="App.TLabel").grid(
            row=1, column=0, columnspan=2
        )

        ttk.Label(self,text="Label", style="App.TLabel").grid(
            row=3, column=0, columnspan=2
        )

        self.project_entry = ttk.Entry(self)
        self.project_entry.grid(
            row=2, column=0, columnspan=2, pady=(0, 10)
        )

        self.label_entry = ttk.Entry(self)
        self.label_entry.grid(
            row=4, column=0, columnspan=2, pady=(0, 10)
        )

        ttk.Button(
            self,
            text="Search",
            command=self.search, 
            style="App.TButton"
        ).grid(row=5, column=0, columnspan=2, pady=5)

        columns = ("project", "label", "time")

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=1
        )

        self.tree.heading("project", text="Project")
        self.tree.heading("label", text="Label")
        self.tree.heading("time", text="Time")

        self.tree.column("project", width=60)
        self.tree.column("label", width=60)
        self.tree.column("time", width=60, anchor="e")

        self.tree.grid(
            row=6, column=0, columnspan=2, pady=10, sticky="nsew"
        )

        ttk.Button(
            self,
            text="Back",
            command=lambda: app.show_frame("log"),
            style="App.TButton"
        ).grid(row=7, column=0, columnspan=2, pady=5)

    def search(self):
        name = self.project_entry.get().strip()
        label = self.label_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Project name is required")
            return
    
        if not label:
            messagebox.showerror("Error", "Label name is required")

        self.refresh(name, label)

    def refresh(self, project_name: str, label_name: str):

        for row in self.tree.get_children():
            self.tree.delete(row)

        summaries = self.app.tracker.repo.get_summary_sql(project_name, label_name)

        if not summaries:
            messagebox.showerror("Error", "No such entry")
            return

        for summary in summaries:
            self.tree.insert(
                "",
                "end",
                values=(
                    summary.project_name,
                    summary.label_name,
                    self._format_duration(summary.total_seconds)
                )
            )

    @staticmethod
    def _format_duration(seconds: int) -> str:
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"

class OverviewFrame(ttk.Frame):
    def __init__(self, app: TimeTrackerApp):
        super().__init__(app, padding=20, style="App.TFrame")
        self.app = app

        self.tree = ttk.Treeview(
            self,
            columns=("time",),
            show="tree headings"
        )

        self.tree.heading("#0", text="Label / Project")
        self.tree.heading("time", text="Time")

        self.tree.column("#0", width=60, anchor="w")
        self.tree.column("time", width=80, anchor="e")

        self.tree.grid(
            row=6, column=0, columnspan=2,
            pady=10, sticky="nsew"
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        ttk.Button(
            self,
            text="Back",
            command=lambda: app.show_frame("log"),
            style="App.TButton"
        ).grid(row=7, column=0, columnspan=2, pady=5)

        self.fill_table()

    def fill_table(self):
        self.tree.delete(*self.tree.get_children())

        summaries = self.app.tracker.repo.get_summary_sql()

        if not summaries:
            return

        labels = {}

        for summary in summaries:

            label = summary.label_name
            project = summary.project_name
            seconds = summary.total_seconds

            if label not in labels:
                label_id = self.tree.insert(
                    "",
                    "end",
                    text=label,
                    values=(self._format_duration(0),),
                    open=False
                )
                labels[label] = {
                    "id": label_id,
                    "total": 0
                }

            self.tree.insert(
                labels[label]["id"],
                "end",
                text=project,
                values=(self._format_duration(seconds),)
            )

            labels[label]["total"] += seconds

        for label, info in labels.items():
            self.tree.item(
                info["id"],
                values=(self._format_duration(info["total"]),)
            )

    @staticmethod
    def _format_duration(seconds: int) -> str:
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    
def gui_main():
    app = TimeTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    gui_main()
