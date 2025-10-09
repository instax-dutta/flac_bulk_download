#!/usr/bin/env python3
import os
from pathlib import Path
from typing import List

from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash, abort
from werkzeug.utils import safe_join


BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"


def list_audio_files(directory: Path) -> List[str]:
    allowed_ext = {".flac", ".mp3", ".wav", ".m4a", ".aac", ".ogg"}
    files: List[str] = []
    if not directory.exists():
        return files
    for entry in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if entry.is_file() and entry.suffix.lower() in allowed_ext:
            files.append(entry.name)
    return files


def create_app() -> Flask:
    app = Flask(__name__)
    # Simple secret key for flash messages (not used for auth)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

    @app.route("/")
    def index():
        tracks = list_audio_files(DOWNLOADS_DIR)
        return render_template("index.html", tracks=tracks)

    @app.get("/audio/<path:filename>")
    def serve_audio(filename: str):
        # Prevent path traversal
        safe_path = safe_join(str(DOWNLOADS_DIR), filename)
        if not safe_path:
            abort(400)
        file_path = Path(safe_path)
        if not file_path.exists() or not file_path.is_file():
            abort(404)
        return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=False)

    @app.post("/delete/<path:filename>")
    def delete_track(filename: str):
        safe_path = safe_join(str(DOWNLOADS_DIR), filename)
        if not safe_path:
            abort(400)
        file_path = Path(safe_path)
        if not file_path.exists() or not file_path.is_file():
            flash("File not found.", "warning")
            return redirect(url_for("index"))
        try:
            file_path.unlink()
            flash(f"Deleted: {file_path.name}", "success")
        except Exception as exc:  # noqa: BLE001
            flash(f"Failed to delete {file_path.name}: {exc}", "error")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    # Run the app for local development
    app.run(host="127.0.0.1", port=5000, debug=True)


