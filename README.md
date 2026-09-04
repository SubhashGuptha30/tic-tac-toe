# AdaptiveRL Tic-Tac-Toe Lab

An interactive reinforcement-learning Tic-Tac-Toe laboratory. Play as
`X` against a persistent Q-learning agent playing as `O`, inspect its
policy and decisions, train it against automated opponents, and evaluate
frozen policy snapshots scientifically.

## Features

- Human-vs-agent online Q-learning with a persistent SQLite Q-table
- Live learning dashboard, strategy evidence, Q-table explorer, episode
  inspector, and decision microscope
- Training Arena with Random, Tactical, and Mixed opponents
- Evaluation Lab with immutable policy snapshots, `epsilon = 0`, no
  learning, deterministic tie breaking, and opponent comparisons

## Requirements

- Windows PowerShell
- Python 3.11 or later
- Node.js 20 or later

If `backend/.venv` does not exist, create it and install dependencies:

```powershell
py -m venv .\backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
```

## Run Locally

Open **two PowerShell terminals** in VS Code. Run every command below
from the project root:

```text
C:\Users\SUBHASH GUPTHA\Desktop\tic-tac-toe
```

### Terminal 1: Backend API

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir .\backend --host 127.0.0.1 --port 8000
```

Wait until the terminal shows:

```text
Application startup complete.
```

Then verify the backend in a browser:

```text
http://127.0.0.1:8000/api/health
```

The response should contain `"status":"online"`.

### Terminal 2: Frontend UI

If this is the first run, install frontend dependencies once:

```powershell
npm.cmd --prefix .\frontend install
```

Start the React/Vite development server:

```powershell
npm.cmd --prefix .\frontend run dev
```

Open the live site in your browser:

```text
http://127.0.0.1:5173
```

Both terminals must remain running while you use the application.

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

This happens when Uvicorn is started from the project root without an
application directory. Use the backend command shown above exactly. The
important part is:

```powershell
--app-dir .\backend
```

Alternatively, change into `backend` first and use:

```powershell
cd .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### The page opens but shows `Backend Offline` or cannot load data

The frontend is running, but the backend is not. Confirm that:

```text
http://127.0.0.1:8000/api/health
```

opens successfully before refreshing `http://127.0.0.1:5173`.

### `WinError 10013` or address/port already in use

Another process already owns port `8000`. In PowerShell, find it with:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  Select-Object OwningProcess
```

Close the old backend process, or use a different port and update
`frontend/src/services/api.ts` to match it.

### Stop the servers

Press `Ctrl+C` in each terminal.

## Verification

Run the backend tests:

```powershell
cd .\backend
.\.venv\Scripts\python.exe -m pytest
```

Build the frontend production bundle:

```powershell
cd ..
npm.cmd --prefix .\frontend run build
```
