# Getting Started with Azure Cost Forecasting Engine

This guide is for people with **no coding experience**. It walks you through every step, from opening a terminal to generating your first cost forecast report.

> **Good news:** you don't need an Azure account to try this tool. It ships with a **demo mode** that runs the full forecasting pipeline on synthetic data, no credentials required. Real Azure credentials are only needed later, if you want to forecast your own subscription's actual spend (see the "Optional: connect your own Azure subscription" section at the end).

---

## Windows

### 1. Open a terminal

Right-click the **Start** button and choose **Terminal** (or **Windows PowerShell** on older Windows versions).

### 2. Check your Python version

```powershell
py --version
```

- If it prints `Python 3.11.x` or higher, continue to step 3.
- If it prints an older version, or you see `'py' is not recognized as the name of a cmdlet, function, script file, or operable program`, Python isn't installed (or wasn't added to your system PATH).

**Install Python:**

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest installer.
2. Run it. On the very first screen, **check the box "Add python.exe to PATH"** at the bottom before clicking Install — easy to miss, and the most common reason `py` isn't recognized afterwards.
3. Close and reopen your terminal, then re-run `py --version` to confirm.

### 3. Download the project

No-Git route:

1. Go to [github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine](https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine).
2. Click the green **Code** button → **Download ZIP**.
3. Extract it (right-click → **Extract All...**), e.g. to `Documents\azure-cost-forecasting-engine`.

Or, with Git:

```powershell
git clone https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine
```

### 4. Move into the folder and install

```powershell
cd Documents\azure-cost-forecasting-engine
pip install -e .
```

(Tip: type `cd ` with a trailing space, then drag the folder from File Explorer into the terminal to auto-fill the path. If `pip` isn't recognized, try `py -m pip install -e .`.)

### 5. Run the demo

```powershell
py cli.py run --demo
```

This generates a forecast from built-in synthetic data and prints a table straight to your terminal, no setup needed beyond what you just did.

---

## Linux

### 1. Open a terminal

Usually `Ctrl+Alt+T`, or search "Terminal" in your application menu.

### 2. Check your Python version

```bash
python3 --version
```

- `Python 3.11.x` or higher → continue to step 3.
- Older or `command not found: python3` → most distributions include Python already; if not, install via your package manager, e.g. Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 3. Download the project

No-Git route: download the ZIP from [github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine](https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine) (green **Code** button → **Download ZIP**) and extract it.

Or, with Git:

```bash
git clone https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine
cd azure-cost-forecasting-engine
```

### 4. Install

```bash
pip install -e .
```

If `pip` isn't found, try `pip3 install -e .` or `python3 -m pip install -e .`.

### 5. Run the demo

```bash
python3 cli.py run --demo
```

---

## macOS

### 1. Open a terminal

Press `Cmd+Space`, type `Terminal`, press Enter.

### 2. Check your Python version

```bash
python3 --version
```

- `Python 3.11.x` or higher → continue to step 3.
- Older or `command not found: python3` → install from [python.org/downloads](https://www.python.org/downloads/) (run the installer with defaults), or via [Homebrew](https://brew.sh): `brew install python@3.12`. Reopen Terminal and re-check.

### 3. Download the project

No-Git route: download the ZIP from [github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine](https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine) (green **Code** button → **Download ZIP**) and extract it (double-click in Finder).

Or, with Git:

```bash
git clone https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine
cd azure-cost-forecasting-engine
```

### 4. Install

```bash
pip install -e .
```

If `pip` isn't found, try `pip3 install -e .` or `python3 -m pip install -e .`.

### 5. Run the demo

```bash
python3 cli.py run --demo
```

<!-- TODO: Screenshot of the demo table output in the terminal -->

---

## What you should see

`... cli.py run --demo` prints a table to your terminal with synthetic daily Azure costs, a 30/60/90-day forecast, any detected anomalies, and cost optimization recommendations, all generated from fake data so you can see exactly what a real report looks like.

Try the other output formats:

```bash
# same commands work on Windows (py cli.py ...) and Linux/macOS (python3 cli.py ...)
python3 cli.py run --demo --format md --output report.md
python3 cli.py run --demo --format json --output report.json
```

Open `report.md` in any text editor, or `report.json` to see the structured data.

---

## Optional: connect your own Azure subscription

To forecast your *actual* Azure spend instead of synthetic data, you need an Azure app registration with the **Cost Management Reader** role. The exact steps are in the "App Registration Setup" section of the main [README.md](README.md). In short:

1. Create an app registration in Entra ID and assign it the `Cost Management Reader` role on your subscription.
2. Copy `.env.example` to `.env` and fill in your Tenant ID, Client ID, Client Secret, and Subscription ID.
3. Run:

```bash
python3 cli.py run --history 90 --format table
```

(Windows: `py cli.py run --history 90 --format table`.)

No write permissions are ever required, and credentials are read only from environment variables, never written to disk or logged.

---

### Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Windows: `'py' is not recognized...` | Python isn't installed, or wasn't added to PATH during install | Reinstall from [python.org](https://www.python.org/downloads/), ticking "Add python.exe to PATH", then reopen the terminal |
| Linux/macOS: `command not found: python3` | Python isn't installed | Linux: `sudo apt install python3` (Debian/Ubuntu) or your distro's equivalent. macOS: install from [python.org](https://www.python.org/downloads/) or `brew install python@3.12` |
| `pip install -e .` fails with a permissions error | Trying to install into a system-protected Python environment | Add `--user` to the command, e.g. `pip install -e . --user`, or ask an experienced user about Python virtual environments |
| `cli.py run` (without `--demo`) fails with an authentication error | Azure credentials in `.env` are missing or incorrect, or the app registration doesn't have the `Cost Management Reader` role | Re-check `.env` against the "App Registration Setup" section in the main [README.md](README.md), or just use `--demo` if you don't need real data yet |
| Windows PowerShell blocks a `.ps1` script with "cannot be loaded because running scripts is disabled on this system" | PowerShell's execution policy blocks unsigned local scripts | Only if you intentionally need to run a `.ps1` helper script: open PowerShell as Administrator and run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then confirm with `Y` |
