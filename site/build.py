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
- The PDFs are published under clean names (David-Adegbola-CV-<Job-Title>[-FI|-EN].pdf), the same names they
  download as; the workflow's david-adegbola-<slug>[-<lang>].pdf files are moved, not kept (David, 2026-11-23).
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
import unicodedata
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
        for suffix, lang in (("", None), ("-fi", "fi"), ("-en", "en")):
            src = out / cv_file_name(new, lang)
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


def file_name(*parts):
    """Download name that HR and ATS handle well (David, 2026-11-23): full name first, document type,
    job title; ASCII only, words joined by hyphens, no spaces, versions or company names.
    e.g. David-Adegbola-CV-Warehouse-Worker-FI.pdf"""
    text = " ".join(p for p in parts if p)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    words = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", text)
    return "-".join(words)[:120] + ".pdf"


def cv_job_title(slug):
    """The CV's English job title (\\cvrole in cv-en.tex), never the internal folder name."""
    tex = REPO / "roles" / slug / "cv-en.tex"
    if tex.is_file():
        m = re.search(r"\\cvrole\{([^}]*)\}", tex.read_text(encoding="utf-8"))
        if m:
            return tex_text(m.group(1))
    return role_title(slug).split(" / ")[-1]


def cv_file_name(slug, lang=None):
    return file_name("David Adegbola CV", cv_job_title(slug), lang.upper() if lang else "")


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

    # favicons: SVG for modern browsers, PNG for Safari, and the iPhone home-screen icon
    for icon in ("favicon.svg", "favicon.png", "apple-touch-icon.png"):
        shutil.copyfile(SITE_SRC / icon, out / icon)

    (out / "index.html").write_text(page.substitute(
        common, title=esc(facts["name"]), eyebrow="Job applications",
        hero='<p class="lead">If I sent you a link, it opens my CV for that job.</p>', body=OWNER_DOOR),
        encoding="utf-8")

    made, rows, taken = [], [], {}
    for d in sorted((REPO / "roles").glob("*/")):
        slug = d.name
        langs = [lang for lang in language.langs(d)
                 if (out / f"david-adegbola-{slug}-{lang}.pdf").exists() or (out / cv_file_name(slug, lang)).exists()]
        if not langs:
            continue
        files = publish(out, slug, langs, taken)
        combined = None in files
        embed = files[None] if combined else files[langs[0]]
        labels = {"fi": "Lataa CV (suomi)", "en": "Download CV (English)"}
        # the main language is the primary button, the other one secondary
        buttons = "".join(f'<a class="btn{" secondary" if i else ""}" href="../../{files[lang]}" download="{files[lang]}" hreflang="{lang}">'
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
        rows.append((slug, title, files, langs))
    downloads(out, page, common, rows)
    return made


def publish(out, slug, langs, taken):
    """Move a role's compiled PDFs (david-adegbola-<slug>[-<lang>].pdf, written by the workflow) to their
    published names, e.g. David-Adegbola-CV-Warehouse-Worker-FI.pdf (David, 2026-11-23: the address is
    the same clean name the file downloads as; internal folder names are never published).
    Returns {None: combined, "fi": ..., "en": ...}. Two roles with the same job title stop the build."""
    files = {}
    for lang in [None] + list(langs):
        src = out / (f"david-adegbola-{slug}-{lang}.pdf" if lang else f"david-adegbola-{slug}.pdf")
        name = cv_file_name(slug, lang)
        if not src.exists() and not (out / name).exists():
            continue
        if taken.setdefault(name, slug) != slug:
            sys.exit(f"{slug} and {taken[name]} would both publish {name}: give one a different \\cvrole")
        if src.exists():  # already moved when the build runs twice on one folder
            shutil.move(src, out / name)
        files[lang] = name
    return files


def downloads(out, page, common, rows):
    """Unlisted page listing every role's PDFs, at the secret path in DOWNLOADS_PATH (skipped when unset)."""
    path = os.environ.get("DOWNLOADS_PATH", "").strip().strip("/")
    if not path:
        return
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", path):
        sys.exit("DOWNLOADS_PATH must be 16-64 letters, digits, _ or -")
    names = {"fi": "suomi", "en": "English"}
    target = out / path
    items = []
    for slug, title, published, langs in rows:
        # a private view page per CV under the secret path (the public employer pages are not linked here)
        embed = published.get(None) or published[langs[0]]
        files = ([("Combined", published[None])] if None in published else []) + \
                [(names[lang], published[lang]) for lang in langs]
        dest = target / "cv" / slug
        dest.mkdir(parents=True, exist_ok=True)
        btns = "".join(f'<a class="btn{" secondary" if i else ""}" href="../../../{f}" download="{f}">{label}</a>'
                       for i, (label, f) in enumerate(files))
        (dest / "index.html").write_text(page.substitute(
            common, title=f"CV – {esc(title)}", eyebrow="CV",
            hero=f'<p class="role">{esc(title)}</p>',
            body=pdf_view(btns, f"../../../{embed}", f"CV: {title}", "CV")), encoding="utf-8")
        links = [f'<a class="btn" href="cv/{slug}/">View</a>'] + \
                [f'<a class="btn secondary" href="../{f}" download="{f}">{label}</a>' for label, f in files]
        items.append(f'<li><p class="role">{esc(title)}</p><p class="buttons">{"".join(links)}</p></li>')
    target.mkdir(parents=True, exist_ok=True)
    letter_rows = letters(target, page, common)
    body = (NEW_JOB + TABS.format(cvs=len(items), letters=len(letter_rows))
            + f'<div class="tabpanel" id="panel-cvs" role="tabpanel" aria-labelledby="tab-cvs"><ul class="downloads">{"".join(items)}</ul></div>'
            + f'<div class="tabpanel" id="panel-letters" role="tabpanel" aria-labelledby="tab-letters" hidden>'
            + (f'<ul class="downloads">{"".join(letter_rows)}</ul>' if letter_rows else '<p>No cover letters yet.</p>')
            + '</div>' + TABS_SCRIPT)
    (target / "index.html").write_text(page.substitute(
        common, title="All CVs", eyebrow="Downloads",
        hero='<p class="lead">Every CV and cover letter, newest build.</p>', body=body),
        encoding="utf-8")


def tex_text(value):
    """Plain text from a short LaTeX string: -- to an en dash, commands and braces removed."""
    value = value.replace("---", "\u2014").replace("--", "\u2013").replace("~", " ")
    value = re.sub(r"\\[A-Za-z]+\*?", "", value)
    return re.sub(r"\s+", " ", value.replace("{", "").replace("}", "")).strip()


def letter_title(app):
    """A letter's title and date from its .tex: the English subject without "Application:" (the Finnish
    one without "Hakemus:" for Finnish-only letters), and the \\recipient date. Falls back to the folder name."""
    for lang, prefix in (("en", r"Application:\s*"), ("fi", r"Hakemus:\s*")):
        tex = app / f"cover-letter-{lang}.tex"
        if not tex.is_file():
            continue
        src = tex.read_text(encoding="utf-8", errors="replace")
        subject = re.search(r"\\subject\{(.+?)\}\s*$", src, re.M)
        date = re.search(r"\\recipient\{([^}]*)\}", src)
        if subject:
            return (re.sub("^" + prefix, "", tex_text(subject.group(1))) or app.name,
                    tex_text(date.group(1)) if date else "")
    return app.name.replace("-", " "), ""


def pdf_view(buttons, embed, label, noun, back="../../"):
    """Body of a private view page: download buttons, the PDF embedded, and a plain link."""
    return (f'<p class="buttons">{buttons}<a class="btn secondary" href="{back}">All downloads</a></p>'
            f'<object class="cv" data="{embed}{esc(VIEWER)}" type="application/pdf" aria-label="{esc(label)}">'
            f'<p>Your browser can\'t show the PDF here. <a href="{embed}">Open the {noun}</a>.</p></object>'
            f'<p class="open"><a href="{embed}">Open the {noun} as a PDF</a></p>')


# Top of the downloads page: start a new application (the "New job" issue form in the private repo)
NEW_JOB = ('<p class="newjob"><a class="btn" href="https://github.com/david-adegbola/cv-applications/issues/new'
           '?template=new-job.yml" target="_blank" rel="noopener">Create a new CV and cover letter</a>'
           '<span>Opens the New job form on GitHub. Paste the job ad; the CV and letter appear here when it\'s done.</span></p>')

TABS = ('<div class="tabs" role="tablist" aria-label="Documents">'
        '<button class="tab" id="tab-cvs" role="tab" aria-selected="true" aria-controls="panel-cvs">CVs <span>{cvs}</span></button>'
        '<button class="tab" id="tab-letters" role="tab" aria-selected="false" aria-controls="panel-letters" tabindex="-1">'
        'Cover letters <span>{letters}</span></button></div>')

# Tabs: click or arrow keys switch; the choice is kept in the address (#letters) so Back and reload keep it
TABS_SCRIPT = """<script>
(function () {
  var tabs = [].slice.call(document.querySelectorAll('[role="tab"]'));
  function show(tab, push) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on); t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
    });
    if (push) history.replaceState(null, "", tab.id === "tab-letters" ? "#letters" : location.pathname);
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { show(t, true); });
    t.addEventListener("keydown", function (e) {
      var k = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (k) { var n = tabs[(i + k + tabs.length) % tabs.length]; n.focus(); show(n, true); }
    });
  });
  if (location.hash === "#letters") show(tabs[1], false);
})();
</script>"""


def letters(target, page, common):
    """Cover letters from the private applications repo, copied in at build time only (never committed here).

    APPLICATIONS_DIR is a checkout of david-adegbola/cv-applications made by the build with a read-only
    token. Each application folder with a combined letter gets a row. Nothing is printed, because the
    public repo's build logs are public (David, 2026-11-23)."""
    src = os.environ.get("APPLICATIONS_DIR", "").strip()
    if not src or not Path(src).is_dir():
        return []
    names = {"cover-letter-combined.pdf": "Combined", "cover-letter-fi.pdf": "suomi", "cover-letter-en.pdf": "English"}
    rows = []
    for app in sorted(p for p in Path(src).iterdir() if (p / "cover-letter-combined.pdf").is_file()):
        dest = target / "letters" / app.name
        dest.mkdir(parents=True, exist_ok=True)
        title, date = letter_title(app)
        # download name: the job title only (the subject up to its first comma), no company name
        job = title.split(",")[0]
        suffix = {"cover-letter-combined.pdf": "", "cover-letter-fi.pdf": "FI", "cover-letter-en.pdf": "EN"}
        links, published = [], {}
        for i, (fname, label) in enumerate(names.items()):
            if (app / fname).is_file():
                dl = file_name("David Adegbola Cover Letter", job, suffix[fname])
                shutil.copyfile(app / fname, dest / dl)
                published[fname] = dl
                links.append(f'<a class="btn{" secondary" if i else ""}" href="letters/{esc(app.name)}/{esc(dl)}" download="{esc(dl)}">{label}</a>')
        # a view page per letter, like the employer pages: the combined letter embedded, downloads above
        embed = esc(published["cover-letter-combined.pdf"])
        view = pdf_view("".join(l.replace(f"letters/{esc(app.name)}/", "") for l in links), embed, f"Cover letter: {title}", "letter", back="../../#letters")
        (dest / "index.html").write_text(page.substitute(
            common, title=f"Cover letter – {esc(title)}", eyebrow="Cover letter",
            hero=f'<p class="role">{esc(title)}</p>', body=view), encoding="utf-8")
        links.insert(0, f'<a class="btn" href="letters/{esc(app.name)}/">View</a>')
        links[1] = links[1].replace('class="btn"', 'class="btn secondary"', 1)
        when = f' <span class="date">{esc(date)}</span>' if date else ""
        rows.append(f'<li><p class="role">{esc(title)}{when}</p><p class="buttons">{"".join(links)}</p></li>')
    return rows


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 site/build.py <output dir, e.g. _site>")
    slugs = build(sys.argv[1])
    print("Employer pages:", ", ".join(f"r/{s}/" for s in slugs) or "none")
    facts = json.loads((REPO / "facts.json").read_text(encoding="utf-8"))
    print("Redirects:", ", ".join(redirects(Path(sys.argv[1]), slugs, esc(facts["name"]))) or "none")
