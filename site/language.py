#!/usr/bin/env python3
"""A role's language setting, from the "- **Language:** ..." line in roles/<role>/job.md.

    fi-first  (default) cv-fi.tex is the main version; combined PDF = Finnish, then English
    en-first  cv-en.tex is the main version; combined PDF = English, then Finnish
    en-only   only cv-en.tex is built; the combined PDF is the English CV on its own

    python3 site/language.py roles/<role>          prints the setting
    python3 site/language.py roles/<role> --langs  prints the languages to build, main first ("fi en")

Used by the GitHub Action, shared/combine.sh and site/build.py, so they all read job.md the same way.
"""

import re
import sys
from pathlib import Path

ORDER = {"fi-first": ["fi", "en"], "en-first": ["en", "fi"], "en-only": ["en"]}
DEFAULT = "fi-first"
# "Language:" only; the "Languages:" line (which files exist) doesn't match
FIELD = re.compile(r"^\W*language\W*:\W*([a-z]+-[a-z]+)", re.I | re.M)


def setting(role_dir):
    job = Path(role_dir) / "job.md"
    m = FIELD.search(job.read_text(encoding="utf-8")) if job.exists() else None
    if not m:
        return DEFAULT
    value = m.group(1).lower()
    if value not in ORDER:
        raise ValueError(f"{job}: Language must be one of {', '.join(ORDER)}, not '{m.group(1)}'")
    return value


def langs(role_dir):
    return ORDER[setting(role_dir)]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python3 site/language.py roles/<role> [--langs]")
    try:
        print(" ".join(langs(sys.argv[1])) if "--langs" in sys.argv else setting(sys.argv[1]))
    except ValueError as e:
        sys.exit(str(e))
