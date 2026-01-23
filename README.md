# Time Tracker – Desktop Application

**Time Tracker** is a simple desktop application written in Python for tracking time spent on projects.  
It allows users to start and stop time tracking, view history, generate summaries, and display an overview grouped by labels and projects.

The application is implemented as a **desktop GUI app using Tkinter**.

---

## Features

- **Start and stop time tracking**
- Assign **projects** and **labels**
- **History view** of all recorded entries
- **Summary** of total time for a selected project and label
- **Overview** grouped by label → project → total time

## Requirements

- Python 3.10+

## Run

```text
python3 app.py
```

## Building Desktop App

The application can be packaged into a standalone .app using PyInstaller.

**Install PyInstaller**

```text
python3 -m pip install pyinstaller
```

**Build**

```text
rm -rf build dist *.spec
python3 -m PyInstaller --onefile --windowed app.py
```

The resulting application will be located in:

```text
 dist/
 ```

 ## Running the app on MacOS

 ```text
 ./dist/app.app/Contents/MacOS/app
```

## Project Structure

```
time-tracker/
├── app.py
├── ui/
│   └── ui.py
├── core/
│   └── tracker.py
├── db/
│   └── repository.py
├── utils/
│   └── time_format.py
└── README.md
```

## Technologies Used

- Python
- Tkinter (GUI)
- SQLite (local database)
- PyInstaller (desktop packaging)