from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from muti_agents import CommentModerator
from tools.search_api.fetch_news import fetch_news_main_text
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

from functools import lru_cache
import hashlib
import threading
import time
import subprocess
import sys
import os
import json

from tools.search_api.fetch_x_news import get_reddit_comments, fetch_reddit_comments

app = Flask(__name__)
CORS(app, resources={
    r"/moderate": {"origins": "*"},
    r"/moderate_stream": {"origins": "*"},
    r"/detect_all": {"origins": "*"},
    r"/detect_all_stream": {"origins": "*"},
    r"/": {"origins": "*"}
})

moderator = CommentModerator()


def _make_sig(news_text: str, comment_text: str) -> str:
    """Hash two long strings to a 40-byte SHA-1 to avoid oversized keys."""
    return hashlib.sha1(f"{news_text}||{comment_text}".encode()).hexdigest()


@lru_cache(maxsize=4_096)
def cached_moderate(news_text: str, comment_text: str):
    return moderator.moderate(news_text, comment_text)


limiter = Limiter(
    app,
    default_limits=["60/minute", "1/second"],
    storage_uri="redis://localhost:6379/0",
)


# Root endpoint for floating window to check service status
@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "running", "message": "Flask service is healthy"})


# Original sync endpoint (unchanged behavior)
@app.route("/moderate", methods=["POST"])
@limiter.limit("3/10 seconds")
def moderate_endpoint():
    """Synchronous single-comment analysis endpoint."""
    data = request.get_json(force=True, silent=True) or {}
    print(data)
    news_text = data.get("news_text", "")
    comment_text = data.get("comment_text", "")
    language = data.get("language", "en")

    if not news_text or not comment_text:
        return jsonify({"ok": False, "msg": "Both news_text and comment_text must be provided."}), 400

    try:
        result = cached_moderate(news_text, comment_text)
        return jsonify({"ok": True, "data": str(result)})
    except Exception as e:
        return jsonify({"ok": False, "msg": f"Processing failed: {e}"}), 500


# Streaming single-comment analysis
@app.route("/moderate_stream", methods=["POST"])
@limiter.limit("3/10 seconds")
def moderate_stream():
    """Streaming single-comment analysis endpoint."""
    data = request.get_json(force=True, silent=True) or {}
    news_text = data.get("news_text", "")
    comment_text = data.get("comment_text", "")
    language = data.get("language", "en")

    if not news_text or not comment_text:
        return jsonify({"ok": False, "msg": "Missing parameters"}), 400

    def generate_progress():
        try:
            # Simulated steps to show progress
            steps = [
                {"progress": 10, "message": "🔍 Initializing analysis...", "status": "processing"},
                {"progress": 25, "message": "📊 Processing comment text...", "status": "processing"},
                {"progress": 45, "message": "🧠 Analyzing logical patterns...", "status": "processing"},
                {"progress": 65, "message": "⚖️ Evaluating fallacy indicators...", "status": "processing"},
                {"progress": 80, "message": "📝 Generating assessment...", "status": "processing"},
                {"progress": 95, "message": "✨ Finalizing results...", "status": "processing"}
            ]

            for step in steps:
                yield f"data: {json.dumps(step)}\n\n"
                time.sleep(1.2)

            # Actual analysis
            result = cached_moderate(news_text, comment_text)

            # Final result
            final_result = {
                "progress": 100,
                "message": "✅ Analysis complete!",
                "status": "completed",
                "result": {"ok": True, "data": str(result)}
            }
            yield f"data: {json.dumps(final_result)}\n\n"

        except Exception as e:
            error_result = {
                "progress": 100,
                "message": "❌ Analysis failed",
                "status": "error",
                "result": {"ok": False, "msg": f"Processing failed: {e}"}
            }
            yield f"data: {json.dumps(error_result)}\n\n"

    return Response(
        generate_progress(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.route("/detect_all", methods=["POST"])
@limiter.limit("3/10 seconds")
def detect_all():
    """Synchronous batch analysis endpoint."""
    data = request.get_json(force=True, silent=True) or {}
    print(data)
    url = data.get("url", "")
    return jsonify({"ok": True, "data": fetch_reddit_comments(url)})


# Streaming batch analysis
@app.route("/detect_all_stream", methods=["POST"])
@limiter.limit("3/10 seconds")
def detect_all_stream():
    """Streaming batch analysis endpoint."""
    data = request.get_json(force=True, silent=True) or {}
    url = data.get("url", "")

    if not url:
        return jsonify({"ok": False, "msg": "Missing URL parameter"}), 400

    def generate_batch_progress():
        try:
            steps = [
                {"progress": 5, "message": "🌐 Fetching Reddit content...", "status": "processing"},
                {"progress": 15, "message": "📃 Parsing comments structure...", "status": "processing"},
                {"progress": 30, "message": "🔍 Analyzing comment batch #1...", "status": "processing"},
                {"progress": 45, "message": "🔍 Analyzing comment batch #2...", "status": "processing"},
                {"progress": 60, "message": "🔍 Analyzing comment batch #3...", "status": "processing"},
                {"progress": 75, "message": "🔍 Analyzing comment batch #4...", "status": "processing"},
                {"progress": 90, "message": "📊 Aggregating analysis results...", "status": "processing"},
                {"progress": 95, "message": "📋 Preparing summary report...", "status": "processing"}
            ]

            for step in steps:
                yield f"data: {json.dumps(step)}\n\n"
                time.sleep(2.5)

            # Actual batch analysis
            result = fetch_reddit_comments(url)

            final_result = {
                "progress": 100,
                "message": "✅ Batch analysis complete!",
                "status": "completed",
                "result": {"ok": True, "data": result}
            }
            yield f"data: {json.dumps(final_result)}\n\n"

        except Exception as e:
            error_result = {
                "progress": 100,
                "message": "❌ Batch analysis failed",
                "status": "error",
                "result": {"ok": False, "msg": f"Processing failed: {e}"}
            }
            yield f"data: {json.dumps(error_result)}\n\n"

    return Response(
        generate_batch_progress(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


def launch_floating_window():
    """Launch the floating-window UI."""

    def run_window():
        # Wait for the Flask service to start up
        time.sleep(2)

        # Check that the floating-window file exists
        floating_window_file = "floating_window.py"
        if os.path.exists(floating_window_file):
            try:
                # Start the floating window
                print("Launching floating-window app...")
                subprocess.Popen([sys.executable, floating_window_file])
                print("Floating-window app started")
            except Exception as e:
                print(f"Failed to launch floating window: {e}")
        else:
            print(f"Floating-window file {floating_window_file} not found")

    # Start the floating window in a background thread
    threading.Thread(target=run_window, daemon=True).start()


# -- 3. Entry point --
if __name__ == "__main__":
    print("Starting the Flask service...")

    # Launch the floating window
    launch_floating_window()

    # host='0.0.0.0' makes it reachable from Docker containers / remote machines;
    # debug=False prevents the server from starting twice due to the reloader
    print("Flask service is running; the floating window will appear shortly...")
    app.run(host="0.0.0.0", port=5000, debug=False)
