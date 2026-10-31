# David Adegbola's CVs

One tailored CV per job role, in Finnish and English, all sharing one LaTeX layout
(`shared/cv-style.sty`). On every push to `main`, GitHub Actions compiles them and publishes one
**employer page** per role to GitHub Pages.

JobDesk, David's private job dashboard, lives in its own private repo. It reads this repo (the
`roles/` folders and `facts.json`) and never writes to it. No job or application data is ever in
this repo.

## Rules for new CVs

All CV rules (workflow, layout, writing, honesty, privacy, canonical facts) are in
[CV-RULES.md](CV-RULES.md). AI agents are pointed there by `AGENTS.md` and `CLAUDE.md`.
`facts.json` is generated from CV-RULES.md (`python3 site/facts.py`) for the employer pages and
JobDesk. CV-RULES.md stays the authority, and the GitHub Action fails if the two differ.

## Employer links

Each role gets one public page: `https://david-adegbola.github.io/cv/r/<role>/`. It shows David's
name, the role title, contact details, the CV (the combined PDF, main language first, embedded) and
a download button per language. Nothing else: no other roles, no jobs, no tracker.

- The root page (`https://david-adegbola.github.io/cv/`) shows only the name, contact details and
  one line. It does **not** list the roles: links are shared one at a time.
- Every public page has `<meta name="robots" content="noindex">`.
- The PDFs keep their old addresses (`…/david-adegbola-<role>.pdf`, `-fi.pdf`, `-en.pdf`), so links
  already sent still work.
- When roles are merged, `site/redirects.json` maps each old role to the one that absorbed it: the old
  employer page redirects there, and the old PDF names serve the new PDFs (same language).
- The repo itself is public, so the `roles/` folders can still be seen on GitHub. This README and
  the site just don't list them.

The pages are built by `site/build.py` from `site/page.html` and `site/style.css`.

## Tests

After compiling the CVs, run `python3 -m unittest discover -s tests -v` to check localized work
dates, PDF text and layout, and employer-page links. PDF extraction checks need Poppler's
`pdftotext`; the GitHub Actions build installs it and runs the same tests.

## Layout

```
cv/
├── site/                        public employer pages: build.py, page.html, style.css, language.py, redirects.json;
│                                facts.py (makes facts.json from CV-RULES.md)
├── shared/
│   ├── cv-style.sty             shared LaTeX layout: \cvrole, \cvlang, \cvline, cventry, \cvphoto, tags,
│   │                            footer only on CVs longer than one page (automatic)
│   ├── combine.sh               makes the one PDF to send (language order from job.md)
│   └── photos/                  profile photo (off in committed CVs)
├── roles/<role>/                cv-fi.tex, cv-en.tex, job.md (public: no employers; sets the language)
├── applications/                git-ignored: application emails and job-details/<role>.md
├── facts.json                   generated from CV-RULES.md by site/facts.py
├── CV-RULES.md                  the rules and canonical facts
├── .github/workflows/build.yml  compiles every CV and publishes the employer pages
└── README.md
```

## Git commit-message safeguard

AI agents must not add AI-generated `Co-authored-by:` trailers; legitimate human co-authors
should remain. David's global git `commit-msg` hook removes AI co-author trailers, so this repo
has no hook of its own. Don't set `core.hooksPath` here: a repo-level setting would stop the
global hook from running.

## Language option

Each role's `job.md` has a line `- **Language:** fi-first`, `en-first` or `en-only` (no line means
fi-first). It decides what is built and which file you send, `david-adegbola-<role>.pdf`:

- **fi-first:** Finnish is the main version; the combined PDF is Finnish, then English.
- **en-first:** English is the main version; the combined PDF is English, then Finnish. For
  employers that work in English.
- **en-only:** only `cv-en.tex` is built (no `cv-fi.tex` needed); the combined PDF is the English
  CV, so the file name stays the same.

The employer page shows the main version first and only the download buttons that exist.
`site/language.py` reads the setting for the GitHub Action, `shared/combine.sh` and the pages.

## Languages

- Each role folder has `cv-en.tex` and, unless the role is en-only, `cv-fi.tex`. The file name sets the language code: `cv-<lang>.tex` is published as `david-adegbola-<role>-<lang>.pdf`.
- Each role's employer page shows one download button per language. Its title comes from the first `# ` heading in `job.md`.
- In the preamble of each CV, `\cvlang{en}` (the default) or `\cvlang{fi}` switches the fixed labels to that language. These are the contact labels, the section titles, "Page X of Y" / "Sivu X / Y", and the word joining job title and employer in `\job` ("at" in English, a comma in Finnish). `\cvlang{fi}` also loads Finnish hyphenation. Use the labels with `\cvt{key}`, for example `\section{\cvt{experience}}` or `\textsc{\cvt{phone}:}`. The available keys are listed in `shared/cv-style.sty`.
- `ä`, `ö` and `å` can be typed directly; the style loads `fontenc` T1 and `inputenc` utf8.

## Profile photo (optional, off by default)

Committed CVs never show the photo (see `CV-RULES.md`). When an application needs one, turn it on **locally only**: add this line to the CV's preamble, next to `\cvrole{...}`, compile, send the PDF, then remove the line again. Never commit it.

```latex
\cvphoto{../../shared/photos/david.jpg}   % add to a CV's preamble to show the photo
```

Remove the line to hide the photo again. With the photo on, it appears as a 3 cm circle (with a thin border in the tag colour) to the left of the name, role and contact details. Without the line, the header is exactly as before. If the file is missing, the CV still compiles without the photo and LaTeX prints a `cv-style` warning.

Each CV's header sits inside `\begin{cvheader} ... \end{cvheader}`; keep that wrapper when you copy a CV. Every `job.md` says `Photo: no`. For Overleaf, also upload the photo and point `\cvphoto{...}` at it, e.g. `\cvphoto{david.jpg}`.

**Replacing the photo file.** `shared/photos/david.jpg` is already committed (metadata stripped, 600×600 px). To replace it, save the new one in the same place, and strip its EXIF/GPS metadata and resize it to at most 600×600 px **before committing**:

```bash
shared/photos/prepare-photo.sh ~/Pictures/my-photo.jpg
```

The script uses ImageMagick (`magick -strip -resize`) or, without it, `sips -Z 600` plus `exiftool -all=`. The workflow strips and resizes photos again before building, but that only protects the PDFs: anything pushed stays in the public git history.

## Add a new role

Read [CV-RULES.md](CV-RULES.md) first; it has the full workflow and rules.

1. Copy an existing role folder, using a lowercase, hyphenated name:
   ```bash
   cp -R roles/salesperson roles/warehouse-worker
   ```
2. In each `cv-<lang>.tex`, change `\cvrole{...}` (the footer's right-hand text) and the title under the name, then tailor the content. Every role needs both `cv-fi.tex` and `cv-en.tex` unless it is en-only (see Language option).
3. Edit `job.md`. Set the `# ` heading to the role name (no company names; it is shown on the public employer page), then add the job type, languages, PDFs, the date, `Photo: no` and notes about the CV. Employers, contacts, ad links, deadlines and status go in the private, git-ignored `applications/job-details/<role>.md`.
4. Commit and push to `main`. The PDFs and the employer page `/r/<role>/` appear automatically.

**Privacy:** this repo is public. Give only phone, email and town in CVs here: no street address, no photo in committed CVs, and write "Available on request" / "Suosittelijat pyydettäessä" instead of naming references.

## Build locally (macOS)

Install [MacTeX](https://www.tug.org/mactex/) (or BasicTeX plus the `libertine`, `fontawesome` and `babel-finnish` packages). Then run `pdflatex` twice from inside the role folder; the second run fills in "Page X of Y":

```bash
cd roles/salesperson
pdflatex cv-fi.tex
pdflatex cv-fi.tex
open cv-fi.pdf
```

Each CV loads the shared style from `../../shared/cv-style.sty`. A harmless "You have requested package `../../shared/cv-style'" warning is expected.

## Edit in Overleaf

1. Create a blank project and upload the role's `cv-<lang>.tex` **and** `shared/cv-style.sty`, both at the top level of the project.
2. Menu → Settings → Compiler: **pdfLaTeX**.
3. Compile. The CV looks for `cv-style.sty` next to itself first and falls back to `../../shared/cv-style`, so no path change is needed. If you put the `.sty` somewhere else, change the `\usepackage{...}` line near the top of the CV to point at it.
4. Copy your changes back into the repo and push.

## Licence and credits

The layout is adapted from [hmemcpy/cv](https://github.com/hmemcpy/cv) (MIT), which is based on the *Professional CV* template by Alessandro Plasmati. See [LICENSE](LICENSE).
