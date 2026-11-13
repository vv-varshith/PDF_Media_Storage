# PDF & Media Vault

A local Flask website to upload, automatically organise, download, delete (move to Trash), and restore files.

## Windows CMD setup

Open Command Prompt and run these commands one at a time:

```cmd
cd /d "C:\Users\vvvar\OneDrive\Desktop\PDF_Media_Storage"
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

If Python 3.12 is not installed, use `python -m venv .venv` instead of the `py -3.12` line.

Open this address in your browser: http://127.0.0.1:5000

Stop the server with `Ctrl+C`.

## Project files

- `app.py` - Flask routes and file management.
- `templates/base.html` - shared page layout and styling.
- `templates/index.html` - upload and file listing page.
- `templates/trash.html` - restore page.
- `requirements.txt` - Python dependencies.
- `storage/` and `trash/` - created automatically when the app starts.

Files are stored on the computer running the app. This starter project is intended for local use, not public internet hosting. Change `SECRET_KEY`, disable debug mode, and add authentication/CSRF protection before exposing it to other users.
