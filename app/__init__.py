"""BG Cleaner — Professional background removal web app."""

import os
import io
import uuid
import time
import zipfile
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
)
from werkzeug.utils import secure_filename

from app.processor import remove_background, _get_session

import sys
import os


def _base_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_base = Path(_base_path())
UPLOAD_DIR = _base / "uploads"
RESULT_DIR = _base / "results"
UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "bmp", "tiff"}
MAX_MB = 10
MAX_BATCH = 20


def create_app() -> Flask:
    # Pre-load the AI model at startup so first request is instant
    print("  Loading AI model...", flush=True)
    _get_session()
    print("  AI model ready!", flush=True)

    # Resolve template/static for frozen builds
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
        tmpl  = str(base / "app" / "templates")
        stat  = str(base / "app" / "static")
    else:
        tmpl  = "templates"
        stat  = "static"

    app = Flask(
        __name__,
        template_folder=tmpl,
        static_folder=stat,
    )
    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32).hex())

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _allowed(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

    def _cleanup(file_id: str):
        """Remove temp files older than 10 min for this id."""
        for folder in (UPLOAD_DIR, RESULT_DIR):
            for p in folder.glob(f"{file_id}.*"):
                if p.stat().st_mtime < time.time() - 600:
                    p.unlink(missing_ok=True)

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/remove-bg", methods=["POST"])
    def api_remove_bg():
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        if not _allowed(file.filename):
            return jsonify({"error": f"File type not allowed. Use: {', '.join(ALLOWED_EXT)}"}), 400

        input_bytes = file.read()
        if len(input_bytes) > MAX_MB * 1024 * 1024:
            return jsonify({"error": f"File too large. Max {MAX_MB} MB."}), 400

        file_id = uuid.uuid4().hex[:12]

        try:
            result_bytes = remove_background(input_bytes, fill_white=True)
        except Exception as exc:
            return jsonify({"error": f"Processing failed: {exc}"}), 500

        result_path = RESULT_DIR / f"{file_id}.jpg"
        result_path.write_bytes(result_bytes)

        _cleanup(file_id)

        return jsonify({
            "success": True,
            "download_url": f"/api/download/{file_id}",
            "preview_url": f"/api/preview/{file_id}",
        })

    @app.route("/api/preview/<file_id>")
    def api_preview(file_id):
        path = RESULT_DIR / f"{file_id}.jpg"
        if not path.exists():
            return "Not found", 404
        return send_file(path, mimetype="image/jpeg")

    @app.route("/api/download/<file_id>")
    def api_download(file_id):
        path = RESULT_DIR / f"{file_id}.jpg"
        if not path.exists():
            return "Not found", 404
        # Use original filename from query string if provided
        original_name = request.args.get("name", "")
        if original_name:
            # Ensure it ends with .jpg
            download_name = Path(original_name).stem + ".jpg"
        else:
            download_name = f"bg-removed-{file_id}.jpg"
        return send_file(
            path,
            mimetype="image/jpeg",
            as_attachment=True,
            download_name=download_name,
        )

    # -----------------------------------------------------------------------
    # Batch Processing
    # -----------------------------------------------------------------------
    @app.route("/api/remove-bg-batch", methods=["POST"])
    def api_remove_bg_batch():
        files = request.files.getlist("images")
        if not files or all(f.filename == "" for f in files):
            return jsonify({"error": "No images uploaded"}), 400

        valid_files = [f for f in files if f.filename != ""]
        if len(valid_files) > MAX_BATCH:
            return jsonify({"error": f"Too many files. Max {MAX_BATCH} at once."}), 400

        results = []
        errors = []

        # Process all files in parallel using threads
        import concurrent.futures

        def _process_one(file):
            original_name = file.filename
            if not _allowed(original_name):
                return None, {"filename": original_name, "error": "File type not allowed"}

            input_bytes = file.read()
            if len(input_bytes) > MAX_MB * 1024 * 1024:
                return None, {"filename": original_name, "error": "File too large (>10 MB)"}

            file_id = uuid.uuid4().hex[:12]
            try:
                result_bytes = remove_background(input_bytes, fill_white=True)
            except Exception as exc:
                return None, {"filename": original_name, "error": str(exc)}

            result_path = RESULT_DIR / f"{file_id}.jpg"
            result_path.write_bytes(result_bytes)

            clean_name = Path(original_name).stem + ".jpg"
            return ({
                "file_id": file_id,
                "original_name": original_name,
                "clean_name": clean_name,
                "download_url": f"/api/download/{file_id}",
                "preview_url": f"/api/preview/{file_id}",
            }), None

        max_workers = min(len(valid_files), 4)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_process_one, f): f for f in valid_files}
            for future in concurrent.futures.as_completed(futures):
                result, error = future.result()
                if result:
                    results.append(result)
                if error:
                    errors.append(error)

        # Generate zip if multiple results
        zip_url = None
        if len(results) > 1:
            zip_id = uuid.uuid4().hex[:12]
            zip_path = UPLOAD_DIR / f"{zip_id}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for r in results:
                    jpg_path = RESULT_DIR / f"{r['file_id']}.jpg"
                    if jpg_path.exists():
                        zf.write(jpg_path, r["clean_name"])
            zip_url = f"/api/download-zip/{zip_id}"

        return jsonify({
            "success": True,
            "results": results,
            "errors": errors,
            "total": len(valid_files),
            "processed": len(results),
            "failed": len(errors),
            "zip_url": zip_url,
        })

    @app.route("/api/download-zip/<zip_id>")
    def api_download_zip(zip_id):
        path = UPLOAD_DIR / f"{zip_id}.zip"
        if not path.exists():
            return "Not found", 404
        return send_file(
            path,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"bg-cleaned-{zip_id}.zip",
        )

    # -----------------------------------------------------------------------
    # ZIP from already-processed files (used by "Download All" button)
    # -----------------------------------------------------------------------
    @app.route("/api/zip-selected", methods=["POST"])
    def api_zip_selected():
        """Accept JSON list of {file_id, name} objects, zip them, return zip."""
        data = request.get_json(silent=True)
        if not data or "files" not in data:
            return jsonify({"error": "No files specified"}), 400

        files = data["files"]
        if not files:
            return jsonify({"error": "Empty file list"}), 400

        zip_id = uuid.uuid4().hex[:12]
        zip_path = UPLOAD_DIR / f"{zip_id}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for entry in files:
                fid = entry.get("file_id", "")
                name = entry.get("name", f"{fid}.jpg")
                src = RESULT_DIR / f"{fid}.jpg"
                if src.exists():
                    # Use original name with .jpg extension
                    arcname = Path(name).stem + ".jpg"
                    zf.write(src, arcname)

        return jsonify({
            "success": True,
            "zip_url": f"/api/download-zip/{zip_id}",
        })

    return app
