# Inventory Management System

## Prerequisites
- Python 3.8+ installed and on your PATH
- VS Code with the **Live Server** extension (for serving `index.html`)

## Install Python packages (Windows `cmd`)
Open a new Command Prompt in the project root and run:

```cmd
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Notes:
- If you prefer PowerShell, activate with `venv\Scripts\Activate.ps1`.
- `requirements.txt` is in the project root.

## Run the API
Start the Flask API in a terminal (keep this running):

```cmd
python api.py
```

By default Flask runs on http://127.0.0.1:5000. The API in this project exposes endpoints under `/api/`.

## Open the Frontend with Live Server (VS Code)
1. In VS Code open the project and then open the file [index.html](index.html).
2. If you have the Live Server extension installed, click **Go Live** in the VS Code status bar or right-click the file and choose **Open with Live Server**.
3. You can also activate the API, and then you can simply run the index.html file with chrome.

Live Server serves files (by default) at http://127.0.0.1:5500 — open that URL in your browser to view `index.html`.

## Notes on CORS & API URL
- This project enables CORS on the Flask API so the frontend served by Live Server can call the API.
- If the frontend expects a different API base URL, update the frontend code to point to `http://127.0.0.1:5000` (or whichever host/port your API is running on).

## Troubleshooting
- If `python` points to Python 2 or is not found, use the full path to the Python 3 executable or `py -3`.
- If package installation fails, ensure the virtual environment is activated and retry `pip install -r requirements.txt`.

If you want, I can also add a simple `.env` or an npm-style script to automate starting the API and Live Server together.
