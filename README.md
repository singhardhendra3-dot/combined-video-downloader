# Combined Video Downloader (Flask)

One local web app that auto-detects **YouTube**, **Facebook**, or
**Instagram** links pasted into a single box, then downloads video (MP4)
or audio-only (MP3). Built on `yt-dlp`, the same engine as your three
standalone CLI downloaders.

## Setup

You already have `ffmpeg` installed and on PATH from the earlier
projects — that's the only system dependency, and it's done.

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

Paste any YouTube / Facebook / Instagram link, choose Video or Audio,
click Download. The browser will save the file through its normal
download flow (same as downloading any file from a website).

## How platform detection works

`detect_platform()` in `app.py` looks at the domain in the URL:
- `youtube.com` / `youtu.be` → YouTube
- `facebook.com` / `fb.watch` → Facebook
- `instagram.com` → Instagram

If the link doesn't match any of these, the app shows an error instead
of guessing.

## Cookies (needed for Instagram, sometimes Facebook)

Same rules as your standalone downloaders:
- **YouTube**: no cookies needed.
- **Facebook**: only needed for private/friends-only videos.
- **Instagram**: needed for almost everything, even public reels.

To set up cookies:
1. Install a browser extension like "Get cookies.txt LOCALLY".
2. Log into the relevant site in that browser.
3. Export cookies for that domain.
4. Save the file into the `cookies/` folder using these **exact names**:
   - `cookies/facebook_cookies.txt`
   - `cookies/instagram_cookies.txt`

The app automatically picks these up if present — no code changes needed.
**Never share these files** — they contain your login session.

## Project structure

```
combined_downloader/
├── app.py                  # Flask app (routes + yt-dlp logic)
├── templates/
│   └── index.html          # Web form UI
├── cookies/                # Put facebook_cookies.txt / instagram_cookies.txt here
├── downloads/              # Created automatically, files auto-deleted after send
└── requirements.txt
```

## Notes on how downloads work

- Each request gets a unique `job_id` prefix so simultaneous downloads
  from different browser tabs don't collide or overwrite each other.
- After the file is sent to your browser, it's automatically deleted
  from the server's `downloads/` folder to save disk space — your
  browser's own Downloads folder will have the saved copy.
- The page shows a "Downloading..." message once you click Download, but
  there's no live progress bar — the button just re-enables once the
  file is ready. For long videos this can take a while; that's expected.

## Troubleshooting

- **"Link not recognized"**: check the URL is a real YouTube/Facebook/Instagram
  link, not a shortened redirect from another app that mangled it.
- **Instagram/Facebook errors mentioning login or availability**: set up
  cookies as described above.
- **Any extraction error**: first try upgrading yt-dlp, since these
  platforms change frequently:
  ```bash
  pip install -U yt-dlp
  ```

## Ideas to extend later

- Add SQLite logging of each download (URL, platform, timestamp, success/fail).
- Add a live progress bar using a background thread + polling endpoint or SSE.
- Add resolution selection for YouTube (like your original CLI tool had).
- Package as a `.exe` with PyInstaller so it runs without opening a terminal.
