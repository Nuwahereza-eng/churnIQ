# Running ChurnIQ on Windows

This guide takes you from a clean Windows 10 or 11 PC to the ChurnIQ app running in your browser. It takes about
15 minutes, most of it waiting for downloads.

ChurnIQ has two parts that run side by side:

- **Backend (API):** Python and FastAPI. It loads the trained model and the dataset.
- **Frontend (website):** React. It runs in your browser and gets everything from the API.

You will keep **two PowerShell windows** open, one for each part.

> All commands below are for **PowerShell**: press <kbd>Win</kbd>, type `PowerShell`, press <kbd>Enter</kbd>.
> Command Prompt equivalents are listed in [Using Command Prompt instead](#using-command-prompt-instead).

---

## 1. Install the tools (once per computer)

You need three free programs:

| Program | Version | Why |
|---|---|---|
| Git | any recent | to download (clone) the project |
| Python | **3.12, 64-bit** | runs the backend and the model |
| Node.js | **22.12 or later** (the LTS installer is fine) | runs the frontend |

**Option A: install with `winget`** (built into Windows 10/11). Run each line, accepting any prompts:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id OpenJS.NodeJS.LTS -e
```

**Option B: install manually** from the websites:

- Git: <https://git-scm.com/download/win> (default options are fine)
- Python 3.12: <https://www.python.org/downloads/windows/>. Choose the *Windows installer (64-bit)* for the
  latest 3.12 release, and on the first screen tick **"Add python.exe to PATH"**.
- Node.js: <https://nodejs.org/> (the **LTS** installer)

**Close PowerShell and open a new window** so it picks up the new programs, then check them:

```powershell
git --version
py -3.12 --version
node --version
npm --version
```

`py -3.12 --version` should print `Python 3.12.x` and `node --version` should print `v22.12` or higher.
If any command is "not recognized", see [Troubleshooting](#troubleshooting).

> Use Python **3.12** specifically. The project pins exact package versions, and these have ready-made Windows
> builds for 64-bit Python 3.12. Other versions may try to compile packages from source and fail.

---

## 2. Download the project

Choose where to keep it (your Documents folder is fine), then clone it:

```powershell
cd $HOME\Documents
git clone https://github.com/Nuwahereza-eng/churnIQ.git
cd churnIQ
```

From now on, every command starts from this `churnIQ` folder unless a step says otherwise.

---

## 3. Set up the backend (once)

Create a private Python environment for the project and install its packages:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

After `Activate.ps1`, your prompt starts with `(.venv)`. That means the project's Python is active.

> **"running scripts is disabled on this system"?** Windows blocks PowerShell scripts by default. Allow them for
> your user account once, then run `.\.venv\Scripts\Activate.ps1` again:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

Then download the dataset (the public IBM Telco Customer Churn sample, about 1 MB):

```powershell
python scripts\download_data.py
```

It saves `data\raw\Telco-Customer-Churn.csv`. Without internet access, download the file by hand as described in
[data/README.md](data/README.md) and save it at that path.

You do **not** need to train the model: the trained model (`models\churn_pipeline.joblib`) and its evaluation
results are already included in the project.

---

## 4. Set up the frontend (once)

```powershell
cd frontend
npm ci
cd ..
```

`npm ci` installs the exact package versions recorded in `package-lock.json`. It takes a minute or two.
Warnings about funding or deprecated packages are normal; errors are not.

---

## 5. Start ChurnIQ

**PowerShell window 1: the backend.** From the `churnIQ` folder:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Wait for `Uvicorn running on http://127.0.0.1:8000`. Leave this window open.

**PowerShell window 2: the frontend.** Open a second PowerShell window, then:

```powershell
cd $HOME\Documents\churnIQ\frontend
npm run dev
```

Wait for `Local: http://localhost:5173/`. Leave this window open too.

**Open <http://localhost:5173>** in your browser. The top bar should show a green
**"Dataset and model ready"** label.

The API's interactive documentation is at <http://127.0.0.1:8000/docs>.

### Stopping and starting again

- **Stop:** click each PowerShell window and press <kbd>Ctrl</kbd>+<kbd>C</kbd>.
- **Start again later:** repeat only [step 5](#5-start-churniq). Steps 1–4 are one-time setup.

---

## Optional extras

All of these run from the `churnIQ` folder with the environment active (`.\.venv\Scripts\Activate.ps1`).

**Run the automated tests**

```powershell
pip install -r requirements-dev.txt
python -m pytest -q

cd frontend
npm test
cd ..
```

**Run the original Streamlit prototype** (a simpler, single-window version of the app):

```powershell
streamlit run app.py
```

It opens at <http://localhost:8501>.

**Retrain the model** (about 5 minutes on a 4-core laptop; this overwrites the files in `models\` and `reports\`):

```powershell
python -m src.train
```

**Run everything with Docker instead.** If you have [Docker Desktop](https://www.docker.com/products/docker-desktop/)
installed, you can skip steps 3–5 entirely:

```powershell
docker build -t churniq .
docker run -p 8000:8000 churniq
```

Then open <http://localhost:8000>. In this mode one container serves both the website and the API.

---

## Using Command Prompt instead

Everything works the same in Command Prompt (`cmd`) except these two commands:

| PowerShell | Command Prompt |
|---|---|
| `.\.venv\Scripts\Activate.ps1` | `.venv\Scripts\activate.bat` |
| `$env:CHURNIQ_API_TARGET = "http://127.0.0.1:8001"` | `set CHURNIQ_API_TARGET=http://127.0.0.1:8001` |

Command Prompt does not have the "running scripts is disabled" restriction.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `git`, `py`, `node` or `npm` "is not recognized" | Close **all** PowerShell windows and open a new one after installing. If it persists, reinstall and make sure the PATH option is ticked. |
| Typing `python` opens the Microsoft Store | Use `py -3.12` for step 3 instead, or turn off the `python.exe` entries in *Settings → Apps → Advanced app settings → App execution aliases*. Inside the activated `.venv`, `python` works normally. |
| "running scripts is disabled on this system" (for `Activate.ps1` or `npm`) | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once, or use Command Prompt. |
| `pip install` tries to build packages and fails (mentions a compiler or "Microsoft Visual C++") | You are not on 64-bit Python 3.12. Delete the `.venv` folder, install Python 3.12 (64-bit) and repeat step 3 with `py -3.12`. |
| Pages show **"Service unavailable"** and window 2 prints `ECONNREFUSED 127.0.0.1:8000` | The backend is not running. Start it in window 1 (step 5) and click **Try again** in the browser. |
| Top bar shows **"Missing: dataset"** | Run `python scripts\download_data.py` (step 3), then restart the backend. |
| `[Errno 10048]` or "address already in use" on port 8000 | Another program uses port 8000. Start the backend with `--port 8001`, and in window 2 run `$env:CHURNIQ_API_TARGET = "http://127.0.0.1:8001"` before `npm run dev`. |
| Port 5173 already in use | Vite picks the next free port automatically. Open the address it prints. |
| `npm ci` fails with an `EBADENGINE` or Node version error | Install Node.js 22.12 or later (step 1), open a new PowerShell window and run `npm ci` again. |
| Windows Firewall asks about Python or Node | Allowing *private networks* is enough; the app only listens on your own computer. |

---

## What runs where

| Address | What it is |
|---|---|
| <http://localhost:5173> | The ChurnIQ website (development server, window 2) |
| <http://127.0.0.1:8000/api/health> | Backend health check: shows whether the dataset, model and results were found |
| <http://127.0.0.1:8000/docs> | Interactive API documentation |

The figures shown come from the public IBM Telco Customer Churn sample dataset, which describes a fictional
telecom provider. See the [README](README.md) for the research background and results.
