#!/bin/sh
# Make the one PDF that is sent for a role, following the Language line in its job.md:
#   fi-first (default): Finnish, then English    en-first: English, then Finnish
#   en-only: the English CV on its own (same file name, so the file to send is always the same)
# Links and text are kept.
# Usage: shared/combine.sh roles/<role> [output.pdf]   (default: roles/<role>/cv-combined.pdf)
# Compile the role's cv-<lang>.tex files first. Needs python3 and, for two languages, pdfunite (poppler).
set -e
dir=${1:?usage: shared/combine.sh roles/<role> [output.pdf]}
out=${2:-$dir/cv-combined.pdf}
langs=$(python3 "$(dirname "$0")/../site/language.py" "$dir" --langs)
pdfs=""
for lang in $langs; do
  if [ ! -f "$dir/cv-$lang.pdf" ]; then
    echo "combine.sh: $dir needs cv-$lang.pdf ($(python3 "$(dirname "$0")/../site/language.py" "$dir")), skipping" >&2
    exit 0
  fi
  pdfs="$pdfs $dir/cv-$lang.pdf"
done
case "$langs" in
  *" "*) pdfunite $pdfs "$out" ;;
  *) cp $pdfs "$out" ;;
esac
echo "combine.sh: wrote $out ($langs)"
