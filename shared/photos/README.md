# Profile photo

`david.jpg` is David's profile photo (metadata stripped, 600×600 px).

**Committed CVs never show it** (see `CV-RULES.md`). To use it for one application, do it locally only:

1. Add this line to the CV's preamble, next to `\cvrole{...}`:
   ```latex
   \cvphoto{../../shared/photos/david.jpg}
   ```
2. Compile twice from the role folder, e.g. `cd roles/<role> && pdflatex cv-fi.tex && pdflatex cv-fi.tex`, and send that PDF. For one combined file, compile both languages and run `shared/combine.sh roles/<role>`.
3. Remove the line again. Do not commit it.

The photo appears as a 3 cm circle to the left of the name. If the file is missing, the CV still compiles without it and LaTeX prints a `cv-style` warning.
For Overleaf, upload `david.jpg` next to the CV and `cv-style.sty` and use `\cvphoto{david.jpg}`.

## Replacing the photo

Strip its metadata (EXIF, GPS location, camera details) and resize it to at most 600×600 px **before committing**:

```bash
shared/photos/prepare-photo.sh ~/Pictures/my-photo.jpg   # writes shared/photos/david.jpg
```

A square, head-and-shoulders photo works best; it is cropped to a circle. Only `david.jpg` can be committed from this folder; `.gitignore` blocks any other image here, so an unprocessed original can't be pushed by mistake.

This repo is public: once a photo is pushed it stays in the git history, even if you delete it later. The build workflow also strips and resizes photos before compiling, but that only protects the PDFs, not the repo.
