#!/usr/bin/env python3
"""Builds the public GitHub Pages site (run by .github/workflows/build.yml after the PDFs are compiled).

    python3 site/build.py _site

- _site/index.html: name, contact and one line. It does NOT list the roles; David shares role links one at a time.
- _site/r/<slug>/index.html: one employer page per role: name, role title, contact, the CV embedded
  (combined FI + EN PDF, or the single language there is), and FI / EN download buttons. Nothing else.
- Every page has <meta name="robots" content="noindex">.
- The PDFs stay where they were (_site/david-adegbola-<slug>[-<lang>].pdf), so old links keep working.

Contact details come from facts.json (generated from CV-RULES.md by app/facts.py). No job or tracker data
is read here; the dashboard's database never reaches this script.
"""

import html
import json
import re
import sys
from pathlib import Path
from string import Template

REPO = Path(__file__).resolve().parent.parent
SITE_SRC = Path(__file__).resolve().parent


def esc(text):
    return html.escape(text or "", quote=True)


def role_title(slug):
    """Public title from job.md's heading, without internal notes such as "(master)"."""
    job = REPO / "roles" / slug / "job.md"
    if job.exists():
        m = re.search(r"^# (.+)$", job.read_text(encoding="utf-8"), re.M)
        if m:
            return re.sub(r"\s*\(master\)\s*$", "", m.group(1)).strip()
    return slug.replace("-", " ").title()


def contact_html(facts):
    phone_href = re.sub(r"\s+", "", facts["phone"])
    return (f'<p class="contact">{esc(facts["location"])}<br>'
            f'<a href="tel:{esc(phone_href)}">{esc(facts["phone"])}</a><br>'
            f'<a href="mailto:{esc(facts["email"])}">{esc(facts["email"])}</a></p>')


def build(out_dir):
    out = Path(out_dir)
    facts = json.loads((REPO / "facts.json").read_text(encoding="utf-8"))
    page = Template((SITE_SRC / "page.html").read_text(encoding="utf-8"))
    style = (SITE_SRC / "style.css").read_text(encoding="utf-8")
    common = {"name": esc(facts["name"]), "contact": contact_html(facts), "style": style}

    (out / "index.html").write_text(page.substitute(
        common, title=esc(facts["name"]),
        body=f'<p class="lead">Job applications. If I sent you a link, it opens my CV for that job.</p>'),
        encoding="utf-8")

    made = []
    for d in sorted((REPO / "roles").glob("*/")):
        slug = d.name
        langs = [lang for lang in ("fi", "en") if (out / f"david-adegbola-{slug}-{lang}.pdf").exists()]
        if not langs:
            continue
        combined = (out / f"david-adegbola-{slug}.pdf").exists()
        embed = f"david-adegbola-{slug}.pdf" if combined else f"david-adegbola-{slug}-{langs[0]}.pdf"
        labels = {"fi": "Lataa CV (suomi)", "en": "Download CV (English)"}
        buttons = "".join(f'<a class="btn" href="../../david-adegbola-{slug}-{lang}.pdf" download hreflang="{lang}">'
                          f'{labels[lang]}</a>' for lang in langs)
        title = role_title(slug)
        body = (f'<p class="role">{esc(title)}</p>'
                f'<p class="buttons">{buttons}</p>'
                f'<object class="cv" data="../../{embed}" type="application/pdf" aria-label="CV: {esc(title)}">'
                f'<p>Your browser can\'t show the PDF here. <a href="../../{embed}">Open the CV</a>.</p></object>'
                f'<p class="open"><a href="../../{embed}">Open the CV as a PDF</a></p>')
        target = out / "r" / slug
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(page.substitute(
            common, title=f"{esc(facts['name'])} – {esc(title)}", body=body), encoding="utf-8")
        made.append(slug)
    return made


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 site/build.py <output dir, e.g. _site>")
    slugs = build(sys.argv[1])
    print("Employer pages:", ", ".join(f"r/{s}/" for s in slugs) or "none")
