# Agent Nudge Reminder

Agent Nudge Reminder is a lightweight Windows desktop assistant for SOC analysts who need periodic nudges to check SIEM/security dashboards.

It runs as a PySide6 desktop app, minimizes to the system tray, and executes reminder actions on a configurable schedule:
- Play a Windows system alert sound
- Show a Windows toast notification
- Open/focus a target URL in your browser
- Refresh the page via cache-busted URL launch

## How people use it

1. Define a recurring reminder (name, minutes, URL).
2. Select preferred nudge methods (sound/notification/browser/refresh).
3. Click **Start** and continue your work.
4. Minimize to tray so the app continues in the background.
5. Receive nudges at each interval and jump back to your target page quickly.

---

## Project structure

```text
agentnudge/
├── main.py
├── ui.py
├── scheduler.py
├── actions.py
├── tray.py
├── requirements.txt
└── README.md
```

---

## Installation (Windows 10/11)

### 1) Ensure Python 3.10+

```powershell
python --version
```

### 2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3) Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Run locally

```powershell
python main.py
```

When launched:
- Fill reminder settings.
- Click **Start**.
- Closing window minimizes to tray (does not stop scheduler).
- Use tray menu **Exit** to stop and close safely.

---

## Build Windows EXE (PyInstaller)

Install PyInstaller:

```powershell
pip install pyinstaller
```

Build command:

```powershell
pyinstaller --noconfirm --clean --onefile --noconsole --name "AgentNudgeReminder" main.py
```

Flag summary:
- `--noconfirm`: overwrite previous build artifacts without prompts.
- `--clean`: clean PyInstaller cache before build.
- `--onefile`: output a single executable.
- `--noconsole`: hide console window for desktop UX.
- `--name`: sets output executable name.

EXE output location:

```text
dist/AgentNudgeReminder.exe
```

---

## Usage walkthrough

1. **Launch app**
   - Run `python main.py` (or open built EXE).
2. **Set reminder**
   - Enter reminder name.
   - Set interval in minutes.
   - Enter valid `http://` or `https://` target URL.
   - Choose action checkboxes.
   - Click **Start**.
3. **Minimize to tray**
   - Click close button; app hides to tray and keeps running.
4. **Alert fires**
   - At each interval, selected actions execute:
     - Windows alert sound plays.
     - Windows notification pops.
     - Browser opens/focuses URL.
     - If enabled, URL is relaunched with timestamp cache-buster.
5. **Exit safely**
   - Right-click tray icon → **Exit**.
   - Scheduler is stopped and application closes.

---

## Troubleshooting

### App starts but no tray icon appears
- Confirm desktop session supports system tray icons.
- Ensure Windows notification area is not hiding it.

### No sound
- Verify system volume and output device.
- Ensure system sounds are enabled in Windows.

### No toast notification
- Ensure Windows notifications are enabled globally and for the app host process.
- Focus Assist / Do Not Disturb may suppress toasts.

### Browser does not open
- Validate URL begins with `http://` or `https://`.
- Ensure a default browser is configured in Windows.

### EXE works but actions fail
- Run from source (`python main.py`) to inspect behavior quickly.
- Rebuild EXE after dependency updates with `--clean`.
