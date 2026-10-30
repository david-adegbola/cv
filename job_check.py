#!/usr/bin/env python3
"""
Weekly Jobly checker for David's 4 job types:
industrial/assembly, construction, warehouse, IT field technician / data centre.

Run from the repo root:  python3 job_check.py
Needs only Python 3 (built into macOS). No installs.

It reads Jobly's public category pages across Finland, waits 10 s between
requests (Jobly's robots.txt asks for that), remembers which jobs you've
already seen (jobs_seen.json), and writes jobs-data.js. Then it opens
index.html, which shows the jobs as a table.

jobs-data.js and jobs_seen.json are git-ignored: job data stays on this
computer and is never pushed. The public GitHub Pages site never shows it.
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

# ----------------------------------------------------------------------------
# SETTINGS: edit these freely
# ----------------------------------------------------------------------------

# Each job type -> list of Jobly category pages (Finland-wide).
# A category URL is https://www.jobly.fi/tyopaikat/<slug>
JOB_TYPES = {
    "Industrial": ["asentaja", "kokoonpanija", "tuotantotyontekija"],
    "Construction": ["rakennustyontekija", "rakennusmies"],
    "Warehouse": ["varastotyontekija", "logistiikkatyontekija"],
    "IT-Data centre": ["it"],
}

# Which CV to send for each job type (roles/<name>/ in this repo)
CV_FOR_TYPE = {
    "Industrial": "industrial-master",
    "Construction": "construction-master",
    "Warehouse": "warehouse-master",
    "IT-Data centre": "it-field-technician",
}

# For broad categories, keep only titles containing one of these words
# (lower-case). Categories not listed here keep every job.
TITLE_MUST_MATCH = {
    "it": ["tuki", "support", "asentaja", "kenttä", "field", "lähituki",
           "helpdesk", "service desk", "teknikko", "technician",
           "datakeskus", "data center", "data centre", "laite"],
}

# Titles containing these words get a warning flag (you lack these for now).
FLAGS = {
    "hitsa": "welding",
    "c-kortti": "C licence",
    "c-kortillinen": "C licence",
    "kuljettaja": "driving",
    "trukki": "forklift",
    "trukin": "forklift",
    "sähköasentaja": "electrician qualification",
    "sähkö": "electrical",
    "kokenut": "wants experience",
    "senior": "senior",
}

# A job anywhere whose title mentions these is filed under IT-Data centre.
DATA_CENTRE_WORDS = ["datakeskus", "data center", "data centre"]

MAX_PAGES = 3          # about 20 jobs per page
DELAY_SECONDS = 10     # Jobly robots.txt asks for 10 s between requests
BASE = "https://www.jobly.fi"
HERE = Path(__file__).resolve().parent
SEEN_FILE = HERE / "jobs_seen.json"
DATA_FILE = HERE / "jobs-data.js"
INDEX_FILE = HERE / "index.html"
USER_AGENT = "Mozilla/5.0 (personal weekly job check; low volume)"

# ----------------------------------------------------------------------------

JOB_PATH = re.compile(r"/(?:en/job|tyopaikka)/([a-z0-9-]+-(\d+))/?$")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "source", "track", "wbr"}
# Class on a job card element -> field it holds
FIELD_CLASSES = {
    "node__title": "title",
    "date": "date",
    "recruiter-company-profile-job-organization": "company",
    "location": "location",
}


class JoblyParser(HTMLParser):
    """Reads Jobly job cards: <article id="node-<id>" about="/tyopaikka/<slug>">
    with the title (h2.node__title), date (span.date), company
    (span.recruiter-company-profile-job-organization) and location (div.location)."""

    def __init__(self):
        super().__init__()
        self.jobs = []
        self._job = None
        self._depth = 0           # element depth inside the current card
        self._field = None        # (field name, depth where it started)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article":
            m = JOB_PATH.search(a.get("about") or "")
            if m:
                self._job = {"id": m.group(2), "url": f"{BASE}/tyopaikka/{m.group(1)}",
                             "title": [], "date": [], "company": [], "location": []}
                self._depth = 0
                self._field = None
                return
        if not self._job or tag in VOID_TAGS:
            return
        self._depth += 1
        if self._field is None:
            classes = (a.get("class") or "").split()
            for cls, field in FIELD_CLASSES.items():
                if cls in classes:
                    self._field = (field, self._depth)
                    break

    def handle_endtag(self, tag):
        if not self._job:
            return
        if tag == "article":
            self._finish()
            return
        if tag in VOID_TAGS:
            return
        if self._field and self._depth <= self._field[1]:
            self._field = None
        self._depth -= 1

    def handle_data(self, data):
        if self._job and self._field:
            text = " ".join(data.split()).strip(" ,")
            if text:
                self._job[self._field[0]].append(text)

    def _finish(self):
        j = self._job
        self._job = None
        title = " ".join(j["title"])
        if not title:
            return
        self.jobs.append({
            "id": j["id"],
            "title": title,
            "url": j["url"],
            "company": " ".join(j["company"]),
            "location": ", ".join(dict.fromkeys(j["location"])),
            "date": to_iso(" ".join(j["date"])),
        })


def to_iso(text):
    """'30.10.2026' -> '2026-10-30'; anything else -> ''."""
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
    if not m:
        return ""
    try:
        return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1))).date().isoformat()
    except ValueError:
        return ""


def ssl_context():
    """Verified HTTPS context. The python.org build of Python on macOS has no CA certificates
    until its 'Install Certificates' step is run, so fall back to macOS's own store."""
    ctx = ssl.create_default_context()
    if not ctx.get_ca_certs() and os.path.exists("/etc/ssl/cert.pem"):
        ctx.load_verify_locations("/etc/ssl/cert.pem")
    return ctx


SSL_CONTEXT = ssl_context()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept-Language": "fi,en"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        print(f"    ! {url} -> HTTP {e.code}")
    except urllib.error.URLError as e:
        print(f"    ! {url} -> {e.reason}")
    return None


def scrape_category(slug, first_request):
    """Return list of jobs for one category, newest first."""
    found, seen_ids = [], set()
    for page in range(MAX_PAGES):
        url = f"{BASE}/tyopaikat/{slug}" + (f"?page={page}" if page else "")
        if not first_request[0]:
            time.sleep(DELAY_SECONDS)
        first_request[0] = False
        print(f"  reading {url}")
        body = fetch(url)
        if not body:
            break
        parser = JoblyParser()
        parser.feed(body)
        new_on_page = [j for j in parser.jobs if j["id"] not in seen_ids]
        if not new_on_page:
            break
        for job in new_on_page:
            seen_ids.add(job["id"])
            found.append(job)
    return found


def keep(slug, title):
    words = TITLE_MUST_MATCH.get(slug)
    return True if not words else any(w in title.lower() for w in words)


def flags_for(title):
    t = title.lower()
    return sorted({label for word, label in FLAGS.items() if word in t})


def load_seen():
    try:
        return json.loads(SEEN_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def main():
    today = date.today().isoformat()
    seen = load_seen()
    jobs, ids = [], set()
    first_request = [True]

    for category, slugs in JOB_TYPES.items():
        print(f"\n{category}")
        for slug in slugs:
            found = scrape_category(slug, first_request)
            kept = [j for j in found if keep(slug, j["title"])]
            print(f"    {slug}: {len(found)} found, {len(kept)} kept")
            for j in kept:
                if j["id"] in ids:
                    continue
                ids.add(j["id"])
                cat = category
                if any(w in j["title"].lower() for w in DATA_CENTRE_WORDS):
                    cat = "IT-Data centre"
                jobs.append({**j, "category": cat, "cv": CV_FOR_TYPE[cat],
                             "flags": flags_for(j["title"]), "is_new": j["id"] not in seen,
                             "source": "Jobly"})

    for job_id in ids:
        seen.setdefault(job_id, today)
    SEEN_FILE.write_text(json.dumps(seen, indent=0, sort_keys=True))

    data = {"updated": datetime.now().isoformat(timespec="seconds"), "jobs": jobs}
    DATA_FILE.write_text("window.JOBS = " + json.dumps(data, ensure_ascii=False, indent=1)
                         + ";\n", encoding="utf-8")

    new = sum(j["is_new"] for j in jobs)
    print(f"\nDone: {len(jobs)} jobs, {new} new. Data: {DATA_FILE.name}")
    for category in JOB_TYPES:
        n = sum(j["category"] == category for j in jobs)
        print(f"  {category}: {n}")
    if not jobs:
        print("No jobs parsed. Jobly may have changed its page layout; "
              "ask Claude to update JoblyParser.")
    webbrowser.open(INDEX_FILE.as_uri())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nStopped.")
