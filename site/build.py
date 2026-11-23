#!/usr/bin/env python3
"""Builds the public GitHub Pages site (run by .github/workflows/build.yml after the PDFs are compiled).

    python3 site/build.py _site

- _site/index.html: name, contact and one line. It does NOT list the roles; David shares role links one at a time.
- _site/r/<slug>/index.html: one employer page per role: name, role title, contact, the CV embedded
  (the combined PDF, main language first) and one download button per language built, main language
  first (no Finnish button for en-only roles; see site/language.py). Nothing else.
- _site/<DOWNLOADS_PATH>/index.html (only when the DOWNLOADS_PATH environment variable is set, from a repo
  secret): an unlisted page for David with every role's downloads. Its address is not in this repo and nothing
  links to it (David, 2026-11-23).
- Every page has <meta name="robots" content="noindex">.
- The PDFs stay where they were (_site/david-adegbola-<slug>[-<lang>].pdf), so old links keep working.
- Merged roles (site/redirects.json): /r/<old>/ redirects to /r/<new>/, and the new PDFs are also published
  under the old file names (combined -> combined, -fi -> -fi, -en -> -en).

Contact details come from facts.json (generated from CV-RULES.md by site/facts.py). No job or tracker data
is read here: JobDesk is a separate private repo, and its database never reaches this one.
"""

import html
import json
import os
import re
import shutil
import sys
from pathlib import Path
from string import Template

import language

REPO = Path(__file__).resolve().parent.parent
SITE_SRC = Path(__file__).resolve().parent
# Open the embedded CV fitted to the box's width with the thumbnail sidebar closed
# (Chrome/Edge: navpanes, view; Firefox: pagemode). Download and "Open" links get the plain PDF.
VIEWER = "#view=FitH&navpanes=0&pagemode=none"


# Root page: a near-invisible "·" for David. It asks for his code (the DOWNLOADS_PATH value) and opens
# the unlisted downloads page; the code is never in the page, and the browser remembers it after one use.
OWNER_DOOR = """<details class="owner"><summary aria-label="Owner access">·</summary>
<form id="owner-form" autocomplete="on"><label for="owner-code">Code</label>
<input id="owner-code" type="password" autocomplete="current-password" spellcheck="false">
<button class="btn" type="submit">Open</button><p id="owner-msg" role="status"></p></form></details>
<script>
(function () {
  var KEY = "cv-downloads-code", d = document.querySelector(".owner"), f = document.getElementById("owner-form"),
      i = document.getElementById("owner-code"), m = document.getElementById("owner-msg");
  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function go(code, remember) {
    if (!/^[A-Za-z0-9_-]{16,64}$/.test(code)) { m.textContent = "Wrong code."; return; }
    var url = "./" + code + "/";
    fetch(url, { method: "HEAD", cache: "no-store" }).then(function (r) {
      if (!r.ok) { m.textContent = "Wrong code."; try { localStorage.removeItem(KEY); } catch (e) {} return; }
      if (remember) { try { localStorage.setItem(KEY, code); } catch (e) {} }
      location.href = url;
    }).catch(function () { m.textContent = "Couldn't check the code. Try again."; });
  }
  d.addEventListener("toggle", function () {
    if (!d.open) return;
    var c = saved();
    if (c) { go(c, false); } else { i.focus(); }
  });
  f.addEventListener("submit", function (e) { e.preventDefault(); m.textContent = ""; go(i.value.trim(), true); });
})();
</script>"""


REDIRECT_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=../{new}/"><link rel="canonical" href="../{new}/">
<title>{name}</title></head>
<body><p>This CV has moved: <a href="../{new}/">open it here</a>.</p>
<script>location.replace("../{new}/" + location.hash)</script></body></html>
"""


def redirects(out, made, name):
    """Old employer pages and PDF names of merged roles point at the role that absorbed them."""
    mapping = json.loads((SITE_SRC / "redirects.json").read_text(encoding="utf-8"))
    done = []
    for old, new in mapping.items():
        if old.startswith("_") or new not in made or (REPO / "roles" / old).exists():
            continue
        target = out / "r" / old
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(REDIRECT_PAGE.format(new=new, name=name), encoding="utf-8")
        for suffix in ("", "-fi", "-en"):
            src = out / f"david-adegbola-{new}{suffix}.pdf"
            if src.exists():
                shutil.copyfile(src, out / f"david-adegbola-{old}{suffix}.pdf")
        done.append(f"r/{old}/ -> r/{new}/")
    return done


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
    return (f'<dl class="contact"><dt>Location</dt><dd>{esc(facts["location"])}</dd>'
            f'<dt>Phone</dt><dd><a href="tel:{esc(phone_href)}">{esc(facts["phone"])}</a></dd>'
            f'<dt>Email</dt><dd><a href="mailto:{esc(facts["email"])}">{esc(facts["email"])}</a></dd></dl>')


def build(out_dir):
    out = Path(out_dir)
    facts = json.loads((REPO / "facts.json").read_text(encoding="utf-8"))
    page = Template((SITE_SRC / "page.html").read_text(encoding="utf-8"))
    style = (SITE_SRC / "style.css").read_text(encoding="utf-8")
    common = {"name": esc(facts["name"]), "contact": contact_html(facts), "style": style}

    (out / "index.html").write_text(page.substitute(
        common, title=esc(facts["name"]), eyebrow="Job applications",
        hero='<p class="lead">If I sent you a link, it opens my CV for that job.</p>', body=OWNER_DOOR),
        encoding="utf-8")

    made, rows = [], []
    for d in sorted((REPO / "roles").glob("*/")):
        slug = d.name
        langs = [lang for lang in language.langs(d) if (out / f"david-adegbola-{slug}-{lang}.pdf").exists()]
        if not langs:
            continue
        combined = (out / f"david-adegbola-{slug}.pdf").exists()
        embed = f"david-adegbola-{slug}.pdf" if combined else f"david-adegbola-{slug}-{langs[0]}.pdf"
        labels = {"fi": "Lataa CV (suomi)", "en": "Download CV (English)"}
        # the main language is the primary button, the other one secondary
        buttons = "".join(f'<a class="btn{" secondary" if i else ""}" href="../../david-adegbola-{slug}-{lang}.pdf" download hreflang="{lang}">'
                          f'{labels[lang]}</a>' for i, lang in enumerate(langs))
        title = role_title(slug)
        body = (f'<p class="buttons">{buttons}</p>'
                f'<object class="cv" data="../../{embed}{esc(VIEWER)}" type="application/pdf" aria-label="CV: {esc(title)}">'
                f'<p>Your browser can\'t show the PDF here. <a href="../../{embed}">Open the CV</a>.</p></object>'
                f'<p class="open"><a href="../../{embed}">Open the CV as a PDF</a></p>')
        target = out / "r" / slug
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(page.substitute(
            common, title=f"{esc(facts['name'])} – {esc(title)}", eyebrow="CV · Ansioluettelo",
            hero=f'<p class="role">{esc(title)}</p>', body=body), encoding="utf-8")
        made.append(slug)
        rows.append((slug, title, combined, langs))
    downloads(out, page, common, rows)
    return made


def downloads(out, page, common, rows):
    """Unlisted page listing every role's PDFs, at the secret path in DOWNLOADS_PATH (skipped when unset)."""
    path = os.environ.get("DOWNLOADS_PATH", "").strip().strip("/")
    if not path:
        return
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", path):
        sys.exit("DOWNLOADS_PATH must be 16-64 letters, digits, _ or -")
    names = {"fi": "suomi", "en": "English"}
    items = []
    for slug, title, combined, langs in rows:
        links = []
        if combined:
            links.append(f'<a class="btn" href="../david-adegbola-{slug}.pdf" download>Combined</a>')
        links += [f'<a class="btn secondary" href="../david-adegbola-{slug}-{lang}.pdf" download>{names[lang]}</a>' for lang in langs]
        items.append(f'<li><p class="role">{esc(title)}</p><p class="buttons">{"".join(links)}'
                     f'<a class="btn secondary" href="../r/{slug}/">Employer page</a></p></li>')
    target = out / path
    target.mkdir(parents=True, exist_ok=True)
    body = f'<h2 class="section">CVs</h2><ul class="downloads">{"".join(items)}</ul>' + letters(target)
    (target / "index.html").write_text(page.substitute(
        common, title="All CVs", eyebrow="Downloads",
        hero='<p class="lead">Every CV and cover letter, newest build.</p>', body=body),
        encoding="utf-8")


def letters(target):
    """Cover letters from the private applications repo, copied in at build time only (never committed here).

    APPLICATIONS_DIR is a checkout of david-adegbola/cv-applications made by the build with a read-only
    token. Each application folder with a combined letter gets a row. Nothing is printed, because the
    public repo's build logs are public (David, 2026-11-23)."""
    src = os.environ.get("APPLICATIONS_DIR", "").strip()
    if not src or not Path(src).is_dir():
        return ""
    names = {"cover-letter-combined.pdf": "Combined", "cover-letter-fi.pdf": "suomi", "cover-letter-en.pdf": "English"}
    rows = []
    for app in sorted(p for p in Path(src).iterdir() if (p / "cover-letter-combined.pdf").is_file()):
        dest = target / "letters" / app.name
        dest.mkdir(parents=True, exist_ok=True)
        links = []
        for i, (fname, label) in enumerate(names.items()):
            if (app / fname).is_file():
                shutil.copyfile(app / fname, dest / fname)
                links.append(f'<a class="btn{" secondary" if i else ""}" href="letters/{esc(app.name)}/{fname}" download>{label}</a>')
        rows.append(f'<li><p class="role">{esc(app.name.replace("-", " "))}</p><p class="buttons">{"".join(links)}</p></li>')
    if not rows:
        return ""
    return f'<h2 class="section">Cover letters</h2><ul class="downloads">{"".join(rows)}</ul>'


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 site/build.py <output dir, e.g. _site>")
    slugs = build(sys.argv[1])
    print("Employer pages:", ", ".join(f"r/{s}/" for s in slugs) or "none")
    facts = json.loads((REPO / "facts.json").read_text(encoding="utf-8"))
    print("Redirects:", ", ".join(redirects(Path(sys.argv[1]), slugs, esc(facts["name"]))) or "none")
