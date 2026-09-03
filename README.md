# SPD-Notifier

A small, **dependency-free** Python backend plus Chrome/Edge extension that
shows ALU **SPD-Hub** opportunities in an in-page modal. SPD-Hub remains the
host interface; Python remains the authenticated feed and future notification
service.

```
SPD-Hub login  ──►  extension  ──►  Python backend  ──►  RSS JSON  ──►  modal
```

## What it does

- Builds the full `job_feed` URL with **all 18 job types** selected
  (internships, fellowships, scholarships, research, volunteer, …).
- Fetches and parses the RSS/Atom XML into a predictable JSON structure:
  `title`, `link`, `summary`, `pub_date` (ISO-8601 UTC), `guid`, `author`,
  `categories`, and any extra fields under `extra`.
- Injects a dashboard modal directly into SPD-Hub with live search, category
  filtering, and a settings page for future alerts.
- Keeps the Python API available for future email/SMS notification workers.
- Handles the SPD-Hub login wall gracefully: if the feed returns the sign-in
  page instead of XML, it returns a clear `auth_required` status rather than
  crashing.

## Requirements

- Python 3.8+ (uses only the standard library — no `pip install` needed).

## Usage

### 1. Print JSON to the terminal

```bash
python spd_notifier.py --json
```

### 2. Save JSON to a file

```bash
python spd_notifier.py --json --output jobs.json
```

### 3. Run the backend

```bash
python spd_notifier.py --serve
# then install extension/ (see below) and open SPD-Hub
```

Stop the server with `Ctrl+C`.

## Authenticating (getting real data)

SPD-Hub requires an **ALU Google sign-in**, so the public feed returns a login
page. The feed checks the WordPress session cookie (`wordpress_logged_in_*`),
which is set as **HttpOnly** — a browser page script _cannot_ read it.

### Fully automatic: browser extension

A bundled Manifest V3 extension (`extension/`) uses the `chrome.cookies` API
to read the HttpOnly session cookie and push it to the backend the instant you
log in. It also injects the opportunities modal directly into SPD-Hub.

1. Run `python spd_notifier.py --serve`.
2. Open `chrome://extensions` (or `edge://extensions`) and enable Developer
   mode.
3. Choose **Load unpacked** and select the project's `extension/` folder.
4. Open SPD-Hub. Click the extension icon to toggle the modal.

On another website, clicking the icon opens SPD-Hub. If you are logged out,
the extension shows a toast; after login, it detects the session and opens the
modal automatically. Full extension details: `extension/README.md`.

### CLI

```bash
# Save the session for future runs
python spd_notifier.py --set-cookies "wordpress_logged_in_abc=...; __cf_bm=...; cf_clearance=..."

# Use it (reads .spd_session.json automatically)
python spd_notifier.py --json
python spd_notifier.py --serve

# Forget the saved session
python spd_notifier.py --clear-cookies
```

> **Security:** the session cookie is a live credential — treat it like a
> password. Never commit `.spd_session.json` (already in `.gitignore`).
> Cookies expire, so refresh them if you see `auth_required` again.

## JSON output shape

```json
{
  "status": "ok",
  "source": "https://spdhub.alueducation.com/?feed=job_feed&...",
  "fetched_at": "2026-08-27T10:27:18+00:00",
  "count": 2,
  "jobs": [
    {
      "title": "Data Analyst Internship",
      "link": "https://spdhub.alueducation.com/job/1",
      "description_html": "<p>Join our <b>analytics</b> team.</p>",
      "summary": "Join our analytics team.",
      "pub_date": "2025-08-25T09:30:00+00:00",
      "guid": "https://spdhub.alueducation.com/job/1",
      "author": "",
      "categories": ["internship", "full-time"],
      "extra": {}
    }
  ]
}
```

`status` is one of: `ok`, `auth_required`, or `error` (with a `message`).

## Project layout

```
SPD-Notifier/
├── spd_notifier.py          # thin CLI entry point (delegates to backend/)
├── backend/                 # dependency-free Python package
│   ├── __init__.py          # re-exports config, feed, storage, server
│   ├── config.py            # job types, feed URL builder, paths, headers
│   ├── feed.py              # fetch + parse RSS/Atom -> clean JSON
│   ├── storage.py           # cookie + settings persistence (sha256 key)
│   └── server.py            # http.server API + serves web/index.html
├── web/
│   └── index.html           # fallback/local dashboard page
├── extension/               # Manifest V3 auto-capture browser extension
│   ├── manifest.json        # ES-module service worker + content script
│   ├── content.js           # content-script loader (Shadow-DOM modal)
│   ├── content/             # split content-script modules
│   │   ├── api.js           # messaging helper to the backend
│   │   ├── modal.js         # opportunities view + job rendering
│   │   ├── settings.js      # settings view + save
│   │   └── style.css        # isolated modal styles
│   ├── js/                  # background service worker modules
│   │   ├── background.js    # cookie capture, toolbar, API proxy
│   │   └── cookies.js       # collect + send SPD-Hub session cookie
│   └── README.md
├── .gitignore               # excludes .spd_session.json (saved cookie)
└── README.md
```
