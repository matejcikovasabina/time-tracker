import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core.model import Project
from core.tracker import TimeTracker
from db.repository import TimeEntryRepository

def gui_main():
    
    repo = TimeEntryRepository()
    tracker = TimeTracker(repo)

    root = tk.Tk()
    root.title("Time Tracker")
    root.geometry("250x300")

    frame = ttk.Frame(root, padding=20)
    frame_history = ttk.Frame(root, padding=20)
    frame_summary = ttk.Frame(root, padding=20)
    frame.pack(expand=True)

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    
    ttk.Label(frame, text="Project").grid(row=0, column=0, columnspan=2, pady=(0, 5))
    project_entry = ttk.Entry(frame, width=10)
    project_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    ttk.Label(frame, text="Label").grid(row=2, column=0, columnspan=2, pady=(0, 5))

    label_entry = ttk.Entry(frame, width=10)
    label_entry.grid(row=3, column=0, columnspan=2, pady=(0, 15))

    time_var = tk.StringVar(value="0.0 s")

    time_label = ttk.Label(
        frame,
        textvariable=time_var
    )
    time_label.grid(row=6, column=0, columnspan=2, pady=10)

    timer_running = False
    active_entry = None

    def on_start():
        name = project_entry.get().strip()
        label = label_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Project name is required")
            return

        try:
            project = Project(id=None, name=name, label=label)

            nonlocal active_entry, timer_running
            active_entry = tracker.start(project) 
            timer_running = True
            messagebox.showinfo("Started", f"Started tracking '{name}'")
            update_timer()
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))


    def on_stop():
        try:
            nonlocal timer_running, active_entry
            entry = tracker.stop()
            timer_running = False
            active_entry = None
            update_entries()
            messagebox.showinfo(
                "Stopped",
                f"Project: {entry.project.name}\n"
                f"Time spent: {entry.duration_seconds()} sec"
            )
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    def history_page():
        frame.pack_forget()
        frame_history.pack(expand=True)

    def summary_page():
        frame.pack_forget()
        frame_summary.pack(expand=True)

    def log_page_history():
        frame_history.pack_forget()
        frame.pack(expand=True)
    
    def log_page_summary():
        frame_summary.pack_forget()
        frame.pack(expand=True)

    def load():
        nonlocal active_entry, timer_running

        active = tracker.get_active()
        if active is None:
            time_var.set("0.0 s")
            return

        active_entry = active
        timer_running = True

        project_entry.delete(0, tk.END)
        project_entry.insert(0, active.project.name)

        label_entry.delete(0, tk.END)
        label_entry.insert(0, active.project.label)

        update_timer()


    ttk.Button(frame, text="Start", command=on_start)\
        .grid(row=4, column=0, pady=5)

    ttk.Button(frame, text="Stop", command=on_stop)\
        .grid(row=4, column=1, pady=5)

    ttk.Button(frame, text="History", command=history_page)\
        .grid(row=7, column=0)
    
    ttk.Button(frame, text="Summary", command=summary_page)\
        .grid(row=7, column=1)
    
    ttk.Button(frame_history, text="Log", command=log_page_history)\
        .grid(row=7, column=0)
    
    ttk.Button(frame_summary, text="Log", command=log_page_summary)\
        .grid(row=7, column=0)
    
    def update_timer():
        if timer_running and active_entry is not None:
            seconds = active_entry.elapsed_seconds()
            time_var.set(f"{seconds:.1f} s")
            print("now:", datetime.now())
            print("start:", active_entry.start)


        root.after(100, update_timer)

    def update_entries():
        project_entry.delete(0, tk.END)
        label_entry.delete(0, tk.END)

        time_var.set("0.0 s")

    load()
    root.mainloop()


if __name__ == "__main__":
    gui_main()
