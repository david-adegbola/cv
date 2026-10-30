# David Adegbola – CVs

One repository, one tailored CV per job role. Every CV shares the same LaTeX layout (`shared/cv-style.sty`) and has its own content in `roles/<role>/cv.tex`.

On every push to `main`, GitHub Actions compiles each role's CV with `pdflatex` and publishes the PDFs, plus an index page, to GitHub Pages:

- **All CVs:** https://david-adegbola.github.io/cv/
- **IT Field Technician:** https://david-adegbola.github.io/cv/david-adegbola-it-field-technician.pdf

Built PDFs are not committed to the repo. Pages serves them.

## Layout

```
cv/
├── shared/cv-style.sty          shared preamble: packages, colours, \sotag, \sotagrow, \job, \sep,
│                                section format, footer, and \cvrole{...}
├── roles/
│   └── it-field-technician/
│       ├── cv.tex               the CV for this role
│       └── job.md               role name, target employers / job ads, date created, notes
├── .github/workflows/build.yml  builds every roles/*/cv.tex and deploys to Pages
├── index.html                   landing page template (the role list is generated at build time)
├── README.md
└── LICENSE
```

Each PDF is published as `david-adegbola-<role-folder>.pdf`. The name shown on the index page comes from the first `# ` heading in that role's `job.md`.

## Add a new role

1. Copy an existing role folder, using a lowercase, hyphenated name:
   ```bash
   cp -R roles/it-field-technician roles/data-centre-technician
   ```
2. Edit `roles/data-centre-technician/cv.tex`. Change `\cvrole{...}` (the footer's right-hand text) and the title under the name, then tailor the content.
3. Edit `roles/data-centre-technician/job.md`. Set the `# ` heading to the role name, then add the target employers / job ads, the date and any notes.
4. Commit and push to `main`. The new PDF and its entry on the index page appear automatically, with no need to edit `index.html`.

## Build locally (macOS)

Install [MacTeX](https://www.tug.org/mactex/) (or BasicTeX plus the `libertine` and `fontawesome` packages). Then run `pdflatex` twice from inside the role folder; the second run fills in "Page X of Y":

```bash
cd roles/it-field-technician
pdflatex cv.tex
pdflatex cv.tex
open cv.pdf
```

`cv.tex` loads the shared style from `../../shared/cv-style.sty`. A harmless "You have requested package `../../shared/cv-style'" warning is expected.

## Edit in Overleaf

1. Create a blank project and upload the role's `cv.tex` **and** `shared/cv-style.sty`, both at the top level of the project.
2. Menu → Settings → Compiler: **pdfLaTeX**.
3. Compile. `cv.tex` looks for `cv-style.sty` next to itself first and falls back to `../../shared/cv-style`, so no path change is needed. If you put the `.sty` somewhere else, change the `\usepackage{...}` line near the top of `cv.tex` to point at it.
4. Copy your changes back into the repo and push.

## Licence and credits

The layout is adapted from [hmemcpy/cv](https://github.com/hmemcpy/cv) (MIT), which is based on the *Professional CV* template by Alessandro Plasmati. See [LICENSE](LICENSE).
