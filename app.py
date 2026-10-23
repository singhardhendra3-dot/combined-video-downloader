"""
Combined Video Downloader (Flask)
-----------------------------------
One web app that auto-detects YouTube / Facebook / Instagram links and
downloads video or audio-only, using yt-dlp under the hood.

Run locally:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import os
import glob
import uuid
from urllib.parse import urlparse

from flask import Flask, render_template, request, send_file, flash, redirect, url_for, after_this_request
import yt_dlp

app = Flask(__name__)
   app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-if-needed")  # only used for flash messages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
COOKIES_DIR = os.path.join(BASE_DIR, "cookies")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(COOKIES_DIR, exist_ok=True)

# Optional cookie files. Instagram almost always needs one; Facebook only
# for private/friends-only content. See README.md for how to create these.
COOKIE_FILES = {
    "facebook": os.path.join(COOKIES_DIR, "facebook_cookies.txt"),
    "instagram": os.path.join(COOKIES_DIR, "instagram_cookies.txt"),
}


def detect_platform(url):
    domain = urlparse(url).netloc.lower()
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    if "facebook.com" in domain or "fb.watch" in domain:
        return "facebook"
    if "instagram.com" in domain:
        return "instagram"
    return None


def build_ydl_opts(platform, media_type, output_template):
    opts = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    cookie_path = COOKIE_FILES.get(platform)
    if cookie_path and os.path.exists(cookie_path):
        opts["cookiefile"] = cookie_path

    if media_type == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        opts["format"] = "bestvideo+bestaudio/best"
        opts["merge_output_format"] = "mp4"

    return opts


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    media_type = request.form.get("media_type", "video")

    if not url:
        flash("Please paste a video link.")
        return redirect(url_for("index"))

    platform = detect_platform(url)
    if not platform:
        flash("Link not recognized. Please paste a YouTube, Facebook, or Instagram link.")
        return redirect(url_for("index"))

    # Unique filename prefix to avoid collisions between simultaneous downloads
    job_id = uuid.uuid4().hex[:8]
    output_template = os.path.join(DOWNLOAD_DIR, f"{job_id}_%(title).100s.%(ext)s")

    ydl_opts = build_ydl_opts(platform, media_type, output_template)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        err_msg = str(e)
        hint = ""
        if platform == "instagram":
            hint = " Instagram usually requires cookies — see README.md."
        elif platform == "facebook":
            hint = " If this is a private video, you may need cookies — see README.md."
        flash(f"Download failed: {err_msg}.{hint}")
        return redirect(url_for("index"))

    # Find the file we just created (job_id prefix makes this unambiguous)
    matches = glob.glob(os.path.join(DOWNLOAD_DIR, f"{job_id}_*"))
    if not matches:
        flash("Download finished but the file could not be located.")
        return redirect(url_for("index"))

    filepath = matches[0]
    filename = os.path.basename(filepath)[len(job_id) + 1:]  # strip job_id prefix for display

    @after_this_request
    def _cleanup(response):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        return response

    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=False, port=5000)
