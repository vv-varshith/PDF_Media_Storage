
import shutil
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    send_from_directory,
    abort,
    flash,
    render_template_string
)
from werkzeug.utils import secure_filename


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = "change-this-secret-key"

BASE_DIR = Path(__file__).resolve().parent

STORAGE_DIR = BASE_DIR / "storage"
TRASH_DIR = BASE_DIR / "trash"

MAX_FILE_SIZE = 500 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


# ==========================================
# FILE CATEGORIES
# ==========================================

FILE_TYPES = {
    "pdf": {
        "pdf"
    },

    "documents": {
        "doc", "docx", "txt", "rtf",
        "xls", "xlsx", "ppt", "pptx", "csv"
    },

    "music": {
        "mp3", "wav", "m4a", "flac",
        "ogg", "aac", "wma"
    },

    "images": {
        "jpg", "jpeg", "png", "gif",
        "bmp", "webp", "svg"
    },

    "videos": {
        "mp4", "mkv", "avi", "mov",
        "webm", "wmv"
    }
}

ALLOWED_CATEGORIES = set(FILE_TYPES.keys())


# Create storage folders

for category in ALLOWED_CATEGORIES:

    (STORAGE_DIR / category).mkdir(
        parents=True,
        exist_ok=True
    )

    (TRASH_DIR / category).mkdir(
        parents=True,
        exist_ok=True
    )


# ==========================================
# CATEGORY DETECTION
# ==========================================

def get_category(filename):

    if "." not in filename:
        return None

    extension = filename.rsplit(".", 1)[-1].lower()

    for category, extensions in FILE_TYPES.items():

        if extension in extensions:
            return category

    return None


# ==========================================
# UNIQUE FILENAME
# ==========================================

def unique_filename(folder, filename):

    folder = Path(folder)

    original = Path(filename)

    name = original.stem
    extension = original.suffix

    new_filename = filename

    while (folder / new_filename).exists():

        new_filename = (
            f"{name}_{uuid4().hex[:8]}{extension}"
        )

    return new_filename


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def index():

    files = {}

    for category in sorted(ALLOWED_CATEGORIES):

        folder = STORAGE_DIR / category

        files[category] = []

        for file in folder.iterdir():

            if file.is_file():

                files[category].append(file.name)

        files[category].sort(key=str.lower)

    return render_template_string("""

<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>PDF Media Storage</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 25px;
    background: #0f172a;
    color: white;
    font-family: Arial, sans-serif;
}

.container {
    max-width: 1100px;
    margin: auto;
}

h1 {
    color: #38bdf8;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
}

.card {
    background: #1e293b;
    padding: 22px;
    margin-top: 22px;
    border-radius: 14px;
}

input, select {
    padding: 12px;
    margin: 7px 0;
    border-radius: 7px;
    border: none;
    max-width: 100%;
}

button, .btn {
    display: inline-block;
    padding: 10px 15px;
    border: none;
    border-radius: 7px;
    background: #0284c7;
    color: white;
    text-decoration: none;
    cursor: pointer;
    margin: 4px;
}

.open {
    background: #16a34a;
}

.download {
    background: #2563eb;
}

.delete {
    background: #dc2626;
}

.file-item {
    background: #334155;
    padding: 13px;
    margin: 10px 0;
    border-radius: 8px;
    overflow-wrap: anywhere;
}

.file-name {
    font-weight: bold;
    margin-bottom: 10px;
}

a {
    text-decoration: none;
}

.search {
    width: 100%;
    padding: 14px;
    background: white;
    color: black;
}

.empty {
    color: #94a3b8;
}

.category-title {
    color: #38bdf8;
}

form.inline {
    display: inline;
}

@media(max-width: 600px) {

    body {
        padding: 12px;
    }

    .card {
        padding: 15px;
    }

    .btn, button {
        margin-top: 8px;
    }

}

</style>

</head>

<body>

<div class="container">

<h1>PDF Media Storage</h1>

<p class="subtitle">
Your Personal File Management System
</p>


{% with messages = get_flashed_messages() %}

    {% for message in messages %}

        <div class="card">
            {{ message }}
        </div>

    {% endfor %}

{% endwith %}


<!-- UPLOAD SECTION -->

<div class="card">

<h2>Upload Files</h2>

<form action="/upload"
method="POST"
enctype="multipart/form-data">

<input type="file"
name="file"
required>

<br>

<select name="category">

<option value="auto">
Automatic Category
</option>

{% for category in categories %}

<option value="{{ category }}">
{{ category|capitalize }}
</option>

{% endfor %}

</select>

<br>

<button type="submit">
Upload File
</button>

</form>

</div>


<!-- SEARCH -->

<div class="card">

<h2>Search Files</h2>

<input
type="text"
id="search"
class="search"
placeholder="Search your files..."
onkeyup="searchFiles()">

</div>


<!-- FILE CATEGORIES -->

{% for category, filenames in files.items() %}

<div class="card">

<h2 class="category-title">
{{ category|capitalize }}
</h2>

{% if filenames %}

    {% for filename in filenames %}

    <div class="file-item">

        <div class="file-name">
            {% if category == "pdf" %}
                📕
            {% elif category == "images" %}
                🖼️
            {% elif category == "music" %}
                🎵
            {% elif category == "videos" %}
                🎬
            {% else %}
                📄
            {% endif %}

            {{ filename }}
        </div>


        <!-- OPEN PDF -->

        {% if category == "pdf" %}

        <a class="btn open"
        href="{{ url_for(
            'view_file',
            category=category,
            filename=filename
        ) }}"
        target="_blank">

        Open PDF

        </a>

        {% endif %}


        <!-- DOWNLOAD -->

        <a class="btn download"
        href="{{ url_for(
            'download_file',
            category=category,
            filename=filename
        ) }}">

        Download

        </a>


        <!-- DELETE -->

        <form class="inline"
        method="POST"
        action="{{ url_for(
            'delete_file',
            category=category,
            filename=filename
        ) }}"
        onsubmit="return confirm('Move this file to Trash?')">

        <button class="delete" type="submit">
        Delete
        </button>

        </form>

    </div>

    {% endfor %}

{% else %}

<p class="empty">
No files available in this category.
</p>

{% endif %}

</div>

{% endfor %}


<!-- TRASH -->

<div class="card">

<h2>Trash</h2>

<a class="btn"
href="/trash">

View Deleted Files

</a>

</div>

</div>


<script>

function searchFiles() {

    let input = document
        .getElementById("search")
        .value.toLowerCase();

    let items = document
        .getElementsByClassName("file-item");

    for (let i = 0; i < items.length; i++) {

        let filename = items[i]
            .innerText.toLowerCase();

        items[i].style.display =
            filename.includes(input) ? "" : "none";

    }

}

</script>

</body>
</html>

""", files=files, categories=sorted(ALLOWED_CATEGORIES))


# ==========================================
# UPLOAD FILES
# ==========================================

@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:

        flash("Please select a file.")

        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":

        flash("No file selected.")

        return redirect(url_for("index"))

    filename = secure_filename(file.filename)

    if not filename:

        flash("Invalid filename.")

        return redirect(url_for("index"))

    detected_category = get_category(filename)

    if detected_category is None:

        flash("Unsupported file format.")

        return redirect(url_for("index"))

    selected_category = request.form.get(
        "category", "auto"
    )

    if selected_category == "auto":

        category = detected_category

    else:

        if selected_category not in ALLOWED_CATEGORIES:

            abort(400)

        if selected_category != detected_category:

            flash("File type does not match category.")

            return redirect(url_for("index"))

        category = selected_category

    folder = STORAGE_DIR / category

    folder.mkdir(parents=True, exist_ok=True)

    filename = unique_filename(folder, filename)

    file.save(folder / filename)

    flash("File uploaded successfully!")

    return redirect(url_for("index"))


# ==========================================
# OPEN PDF IN BROWSER
# ==========================================

@app.route("/view/<category>/<filename>")
def view_file(category, filename):

    if category not in ALLOWED_CATEGORIES:

        abort(404)

    if category != "pdf":

        abort(404)

    folder = STORAGE_DIR / category

    file_path = folder / filename

    if not file_path.is_file():

        abort(404)

    response = send_from_directory(
        folder,
        filename,
        as_attachment=False,
        mimetype="application/pdf"
    )

    response.headers["X-Content-Type-Options"] = "nosniff"

    return response


# ==========================================
# DOWNLOAD FILE
# ==========================================

@app.route("/download/<category>/<filename>")
def download_file(category, filename):

    if category not in ALLOWED_CATEGORIES:

        abort(404)

    folder = STORAGE_DIR / category

    if not (folder / filename).is_file():

        abort(404)

    return send_from_directory(
        folder,
        filename,
        as_attachment=True
    )


# ==========================================
# DELETE FILE
# ==========================================

@app.route(
    "/delete/<category>/<filename>",
    methods=["POST"]
)
def delete_file(category, filename):

    if category not in ALLOWED_CATEGORIES:

        abort(404)

    source = STORAGE_DIR / category / filename

    if not source.is_file():

        abort(404)

    trash_folder = TRASH_DIR / category

    trash_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    new_name = unique_filename(
        trash_folder,
        filename
    )

    shutil.move(
        str(source),
        str(trash_folder / new_name)
    )

    flash("File moved to Trash.")

    return redirect(url_for("index"))


# ==========================================
# VIEW TRASH
# ==========================================

@app.route("/trash")
def view_trash():

    deleted_files = {}

    for category in sorted(ALLOWED_CATEGORIES):

        folder = TRASH_DIR / category

        deleted_files[category] = []

        if folder.exists():

            deleted_files[category] = sorted(
                [
                    file.name
                    for file in folder.iterdir()
                    if file.is_file()
                ],
                key=str.lower
            )

    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>Trash - PDF Media Storage</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<style>

body {
    background: #0f172a;
    color: white;
    font-family: Arial;
    padding: 25px;
}

.card {
    background: #1e293b;
    padding: 20px;
    margin: 15px 0;
    border-radius: 10px;
}

button, a {
    padding: 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    color: white;
    background: #0284c7;
    text-decoration: none;
}

</style>

</head>

<body>

<h1>Trash - Deleted Files</h1>

{% for category, filenames in deleted_files.items() %}

<div class="card">

<h2>{{ category|capitalize }}</h2>

{% if filenames %}

    {% for filename in filenames %}

    <p>

    {{ filename }}

    <form method="POST"
    action="{{ url_for(
        'restore_file',
        category=category,
        filename=filename
    ) }}">

    <button type="submit">
    Restore
    </button>

    </form>

    </p>

    {% endfor %}

{% else %}

<p>No deleted files.</p>

{% endif %}

</div>

{% endfor %}

<a href="/">Back to Home</a>

</body>

</html>

""", deleted_files=deleted_files)


# ==========================================
# RESTORE FILE
# ==========================================

@app.route(
    "/restore/<category>/<filename>",
    methods=["POST"]
)
def restore_file(category, filename):

    if category not in ALLOWED_CATEGORIES:

        abort(404)

    source = TRASH_DIR / category / filename

    if not source.is_file():

        abort(404)

    destination_folder = STORAGE_DIR / category

    destination_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    new_name = unique_filename(
        destination_folder,
        filename
    )

    shutil.move(
        str(source),
        str(destination_folder / new_name)
    )

    flash("File restored successfully.")

    return redirect(url_for("view_trash"))


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found(error):

    return "404 - File not found.", 404


@app.errorhandler(413)
def file_too_large(error):

    return "File exceeds the 500 MB upload limit.", 413


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
