import tkinter as tk
from tkinter import ttk, messagebox

from core.model import Project
from core.tracker import TimeTracker
from db.repository import TimeEntryRepository
from utils.time_format import format_duration

class Frames:
    LOG = "log"
    HISTORY = "history"
    SUMMARY = "summary"
    OVERVIEW = "overview"


class TimeTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self._setup_style()
        self._setup_state()
        self._setup_window()
        self._setup_frames()

        self.show_frame(Frames.LOG)
        self.load_active()
        self.update_timer()
    
    def _setup_style(self):
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

    def _setup_state(self):
        self.repo = TimeEntryRepository()
        self.tracker = TimeTracker(self.repo)

        self.active_entry = None
        self.timer_running = False
        self.time_var = tk.StringVar(value="0.0 s")

    def _setup_window(self):
        self.title("Time Tracker")
        self.geometry("250x300")

    def _setup_frames(self):
        self.frames = {}
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

        if name in (Frames.HISTORY, Frames.OVERVIEW):
            frame.refresh()

    def load_active(self):
        active = self.tracker.get_active()
        if active:
            self.active_entry = active
            self.timer_running = True
            self.frames["log"].fill_from_entry(active)

    def update_timer(self):
        if not self.timer_running or not self.active_entry:
            return

        seconds = self.active_entry.elapsed_seconds()
        self.time_var.set(format_duration(seconds))
        self.after(500, self.update_timer)

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        self.time_var.set("00:00:00")

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
                   command=lambda: app.show_frame(Frames.HISTORY), style="App.TButton")\
            .grid(row=6, column=0)

        ttk.Button(self, text="Summary",
                   command=lambda: app.show_frame(Frames.SUMMARY), style="App.TButton")\
            .grid(row=6, column=1)
        
        ttk.Button(self, text="Overview", command=lambda: app.show_frame(Frames.OVERVIEW),style="App.TButton")\
            .grid(row=8, column=0, columnspan=2, pady=10)

    def start(self):
        name = self.project_entry.get().strip()
        label = self.label_entry.get().strip()

        try:
            project = Project(id=None, name=name, label=label)
            self.app.active_entry = self.app.tracker.start(project)
            self.app.timer_running = True
            messagebox.showinfo("Started", f"Started tracking '{name}'")
        except (ValueError, RuntimeError) as e:
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

        ttk.Label(self, text="History", style="App.TLabel").pack(pady=5)

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

        self.tree.pack(fill="both", expand=True, pady=10)

        ttk.Button(
            self,
            text="Back",
            command=lambda: app.show_frame(Frames.LOG), style="App.TButton"
        ).pack()

        self.tree.bind("<Button-2>", self.on_right_click)   # macOS
        self.tree.bind("<Button-3>", self.on_right_click)   # Windows / Linux


    def on_right_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        entry_id = int(item_id)

        answer = messagebox.askyesno(
            "Delete entry",
            "Delete selected time entry?"
        )

        if not answer:
            return

        ok = self.app.tracker.delete(entry_id)

        if ok:
            self.refresh()
        else:
            messagebox.showerror("Error", "Failed to delete entry")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        entries = self.app.tracker.history()

        for entry in entries:
            self.tree.insert(
                "",
                "end",
                iid=str(entry.id),
                values=(
                    entry.project.name,
                    entry.project.label,
                    format_duration(entry.duration_seconds())
                )
            )

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
            command=lambda: app.show_frame(Frames.LOG),
            style="App.TButton"
        ).grid(row=7, column=0, columnspan=2, pady=5)

    def search(self):
        try:
            self.refresh(
                self.project_entry.get().strip(),
                self.label_entry.get().strip()
            )
        except ValueError as e:
            messagebox.showerror("Error", str(e))


    def refresh(self, project_name: str, label_name: str):

        for row in self.tree.get_children():
            self.tree.delete(row)

        summaries = self.app.tracker.get_project_summary(project_name, label_name)

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
                    format_duration(summary.total_seconds)
                )
            )

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
            pady=5, sticky="nsew"
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        ttk.Button(
            self,
            text="Back",
            command=lambda: app.show_frame(Frames.LOG),
            style="App.TButton"
        ).grid(row=7, column=0, columnspan=2, pady=5)

        self.fill_table()

    def refresh(self):
        self.fill_table()

    def fill_table(self):
        self.tree.delete(*self.tree.get_children())

        summaries = self.app.tracker.get_overview_summary()

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
                    values=(format_duration(0),),
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
                values=(format_duration(seconds),)
            )

            labels[label]["total"] += seconds

        for label, info in labels.items():
            self.tree.item(
                info["id"],
                values=(format_duration(info["total"]),)
            )
    
def gui_main():
    app = TimeTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    gui_main()
