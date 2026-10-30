#!/bin/sh
# Join a role's two language versions into one PDF, so a single file can be sent:
# Finnish (the main version) first, then English. Links and text are kept.
# Usage: shared/combine.sh roles/<role> [output.pdf]   (default: roles/<role>/cv-combined.pdf)
# Compile cv-fi.tex and cv-en.tex first. Needs pdfunite (poppler).
set -e
dir=${1:?usage: shared/combine.sh roles/<role> [output.pdf]}
out=${2:-$dir/cv-combined.pdf}
if [ ! -f "$dir/cv-fi.pdf" ] || [ ! -f "$dir/cv-en.pdf" ]; then
  echo "combine.sh: $dir needs both cv-fi.pdf and cv-en.pdf, skipping" >&2
  exit 0
fi
pdfunite "$dir/cv-fi.pdf" "$dir/cv-en.pdf" "$out"
echo "combine.sh: wrote $out"
