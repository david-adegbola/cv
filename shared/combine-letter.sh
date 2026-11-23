#!/bin/sh
# Make the one cover-letter PDF that is sent for a role, in the same language order as its CV
# (the Language line in roles/<role>/job.md): fi-first Finnish then English, en-first English
# then Finnish, en-only English alone. Letters are private, so they live in applications/<role>/.
# Usage: shared/combine-letter.sh <role-slug> <application-folder>
#   e.g. shared/combine-letter.sh warehouse-master warehouse-master-examplecorp-tampere
#   writes applications/<application-folder>/cover-letter-combined.pdf (one folder per application,
#   CV-RULES section 9); the role only sets the language order
# Compile the cover-letter-<lang>.tex files first. Needs python3 and, for two languages, pdfunite.
set -e
role=${1:?usage: shared/combine-letter.sh <role-slug> <application-folder>}
app=${2:?usage: shared/combine-letter.sh <role-slug> <application-folder>}
root=$(cd "$(dirname "$0")/.." && pwd)
dir="$root/applications/$app"
out="$dir/cover-letter-combined.pdf"
langs=$(python3 "$root/site/language.py" "$root/roles/$role" --langs)
pdfs=""
for lang in $langs; do
  if [ ! -f "$dir/cover-letter-$lang.pdf" ]; then
    echo "combine-letter.sh: $dir needs cover-letter-$lang.pdf" >&2
    exit 1
  fi
  pdfs="$pdfs $dir/cover-letter-$lang.pdf"
done
case "$langs" in
  *" "*) pdfunite $pdfs "$out" ;;
  *) cp $pdfs "$out" ;;
esac
echo "combine-letter.sh: wrote $out ($langs)"
