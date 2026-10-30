# How to turn the photo on for a CV

The profile photo is stored at `shared/photos/david.jpg` (metadata stripped, 600×600 px). It is **off by default**. Each CV language file has its own switch, so you can choose per role and per language.

## Turn it on

**1. Open the CV file you want:**

| CV | File |
|---|---|
| IT Field Technician (EN) | `roles/it-field-technician/cv-en.tex` |
| Salesperson (EN) | `roles/salesperson/cv-en.tex` |
| Myyjä (FI) | `roles/salesperson/cv-fi.tex` |

**2. Add one line under `\cvrole{...}`** near the top, before `\begin{document}`:

```latex
\cvrole{Salesperson}
\cvphoto{../../shared/photos/david.jpg}
```

**3. In that role's `job.md`, change `Photo: no` to `Photo: yes`.**

**4. Check it locally** (optional), from inside the role folder:

```bash
cd roles/salesperson && pdflatex cv-en.tex && pdflatex cv-en.tex && open cv-en.pdf
```

**5. Commit and push.** The GitHub Action rebuilds, and the live PDF shows the photo:

```bash
git commit -am "Salesperson EN: show photo" && git push
```

## Turn it off again

Delete the `\cvphoto{...}` line, set `Photo: no` in `job.md`, then commit and push.

## Good to know

- **English and Finnish are separate files.** If you want the photo on both Salesperson versions, add the line to both `cv-en.tex` and `cv-fi.tex`.
- **Overleaf:** upload `david.jpg` next to the CV and `cv-style.sty`, then use `\cvphoto{david.jpg}` instead.
- **New roles:** copying a role folder copies its photo setting too. Add or remove the line as needed.
- **Missing photo file:** the CV still compiles, just without the photo, and LaTeX prints a `cv-style` warning.
- **Header wrapper:** the CV's header must sit inside `\begin{cvheader} ... \end{cvheader}`; every current CV already has it.
- **Replacing the photo:** run `shared/photos/prepare-photo.sh ~/Pictures/new-photo.jpg` before committing. It strips EXIF/GPS metadata and resizes to at most 600×600 px. This repo is public, and anything pushed stays in its git history.
