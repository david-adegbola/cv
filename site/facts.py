"""Generates facts.json from CV-RULES.md sections 6 and 7 (the authority).

    python3 site/facts.py            # after editing sections 6 or 7; commit facts.json with it
    python3 site/facts.py --check    # fails if facts.json is out of date (run by the GitHub Action)

facts.json gives the employer pages their contact details (site/build.py) and is read by JobDesk,
the private dashboard in its own repo.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES_FILE = REPO / "CV-RULES.md"
FACTS_FILE = REPO / "facts.json"
PUBLIC_BASE = "https://david-adegbola.github.io/cv"


def _section(text, number):
    m = re.search(rf"^## {number}\..*?(?=^## \d+\.|\Z)", text, re.S | re.M)
    return m.group(0) if m else ""


def _joined(text):
    """Join markdown continuation lines so each bullet is one line."""
    return re.sub(r"\n[ \t]+(?=[^\s*-])", " ", text)


def _find(pattern, text, label):
    m = re.search(pattern, text, re.S)
    if not m:
        raise ValueError(f"CV-RULES.md: could not find {label}")
    return m.group(1).strip()


def parse_rules(path=RULES_FILE):
    text = path.read_text(encoding="utf-8")
    s6 = _joined(_section(text, 6))
    s7 = _joined(_section(text, 7))
    not_held = _find(r"Not held:\s*(.+?)\.\n", s6, "the 'Not held' list")
    not_held = [re.sub(r"\s*\(.*?\)", "", x).strip() for x in re.split(r",\s*", not_held)]
    not_confirmed = re.findall(r"^\s*- ([^:\n]+?): NOT confirmed", s6, re.M)
    return {
        "source": "CV-RULES.md (sections 6 and 7)",
        "name": _find(r"Name:\s*([^,]+),", s7, "the name"),
        "age": int(_find(r"age (\d+)", s7, "the age")),
        "location": _find(r"lives in (.+?)\.\s", s7, "the location"),
        "phone": _find(r"Phone (\+[\d ]+\d)", s7, "the phone number"),
        "email": _find(r"email (\S+@\S+?)\.\s", s7, "the email"),
        "languages": _find(r"Languages:\s*(.+?)\.\n", s7, "the languages"),
        "cards": [_find(r"Cards:\s*([^.(]+(?:\([^)]*\))?)", s7, "the cards")],
        "not_held": not_held,
        "not_confirmed": not_confirmed,
        "public_base": PUBLIC_BASE,
    }


def write():
    facts = parse_rules()
    FACTS_FILE.write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return facts


def check():
    stored = json.loads(FACTS_FILE.read_text(encoding="utf-8"))
    live = parse_rules()
    diff = sorted(k for k in set(live) | set(stored) if live.get(k) != stored.get(k))
    if diff:
        sys.exit(f"facts.json is out of date ({', '.join(diff)}). Run: python3 site/facts.py and commit it.")
    print("facts.json matches CV-RULES.md")


if __name__ == "__main__":
    try:
        if "--check" in sys.argv:
            check()
            sys.exit()
        f = write()
    except ValueError as e:
        sys.exit(str(e))
    print(f"Wrote {FACTS_FILE.name}:")
    print(json.dumps(f, ensure_ascii=False, indent=2))
