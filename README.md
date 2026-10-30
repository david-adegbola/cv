# David Adegbola – CVs

One repository, one tailored CV per job role, each in English and (when available) Finnish. Every CV shares the same LaTeX layout (`shared/cv-style.sty`) and has its own content in `roles/<role>/cv-<lang>.tex`.

On every push to `main`, GitHub Actions compiles each CV with `pdflatex` and publishes the PDFs, plus an index page, to GitHub Pages:

- **All CVs:** https://david-adegbola.github.io/cv/
- **IT Field Technician (English):** https://david-adegbola.github.io/cv/david-adegbola-it-field-technician-en.pdf
- **Salesperson (English):** https://david-adegbola.github.io/cv/david-adegbola-salesperson-en.pdf
- **Myyjä (Suomi):** https://david-adegbola.github.io/cv/david-adegbola-salesperson-fi.pdf

Built PDFs are not committed to the repo. Pages serves them.

## Layout

```
cv/
├── shared/cv-style.sty          shared preamble: packages, colours, \sotag, \sotagrow, \job, \sep,
│                                section format, footer, \cvrole{...} and \cvlang{en|fi}
├── roles/
│   ├── it-field-technician/
│   │   ├── cv-en.tex            English CV for this role
│   │   └── job.md               role name, target employers / job ads, date created, notes
│   └── salesperson/
│       ├── cv-en.tex
│       ├── cv-fi.tex            Finnish CV for this role
│       └── job.md
├── .github/workflows/build.yml  builds every roles/*/cv-*.tex and deploys to Pages
├── index.html                   landing page template (the role list is generated at build time)
├── README.md
└── LICENSE
```

## Languages

- Each role folder has `cv-en.tex` and, when there is a Finnish version, `cv-fi.tex`. The file name sets the language code: `cv-<lang>.tex` is published as `david-adegbola-<role>-<lang>.pdf`.
- On the index page each role shows one button per language ("English", "Suomi"). The role name comes from the first `# ` heading in its `job.md`.
- In the preamble of each CV, `\cvlang{en}` (the default) or `\cvlang{fi}` switches the fixed labels to that language. These are the contact labels, the section titles, "Page X of Y" / "Sivu X / Y", and the word joining job title and employer in `\job` ("at" in English, a comma in Finnish). `\cvlang{fi}` also loads Finnish hyphenation. Use the labels with `\cvt{key}`, for example `\section{\cvt{experience}}` or `\textsc{\cvt{phone}:}`. The available keys are listed in `shared/cv-style.sty`.
- `ä`, `ö` and `å` can be typed directly; the style loads `fontenc` T1 and `inputenc` utf8.

## Add a new role

1. Copy an existing role folder, using a lowercase, hyphenated name:
   ```bash
   cp -R roles/salesperson roles/warehouse-worker
   ```
2. In each `cv-<lang>.tex`, change `\cvrole{...}` (the footer's right-hand text) and the title under the name, then tailor the content. Delete `cv-fi.tex` if there is no Finnish version yet.
3. Edit `job.md`. Set the `# ` heading to the role name, then add the target employers / job ads, the date and any notes.
4. Commit and push to `main`. The new PDFs and their entry on the index page appear automatically, with no need to edit `index.html`.

**Privacy:** this repo is public. Give only phone, email and town in CVs here: no street address, no photo, and write "Available on request" / "Suosittelijat pyydettäessä" instead of naming references.

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
