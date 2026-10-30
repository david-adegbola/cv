#!/bin/sh
# Prepare a profile photo for this public repo: strip all EXIF/GPS metadata,
# fix rotation and resize to at most 600x600 px.
#   shared/photos/prepare-photo.sh ~/Pictures/me.jpg            -> shared/photos/david.jpg
#   shared/photos/prepare-photo.sh ~/Pictures/me.jpg other.jpg  -> shared/photos/other.jpg
set -eu
[ $# -ge 1 ] || { echo "usage: $0 <source image> [output name, default david.jpg]" >&2; exit 1; }
src=$1
out="$(dirname "$0")/${2:-david.jpg}"

if command -v magick >/dev/null 2>&1; then
  magick "$src" -auto-orient -strip -resize '600x600>' -quality 90 "$out"
elif command -v exiftool >/dev/null 2>&1; then
  # macOS without ImageMagick: sips resizes/converts, exiftool removes the metadata
  sips -s format jpeg -Z 600 "$src" --out "$out" >/dev/null
  exiftool -overwrite_original -all= "$out" >/dev/null
else
  echo "Need ImageMagick (brew install imagemagick) or exiftool (brew install exiftool)." >&2
  exit 1
fi

echo "Wrote $out"
if command -v exiftool >/dev/null 2>&1; then
  exiftool -G -a -s "$out" | grep -Ei 'GPS|EXIF|Make|Model|DateTimeOriginal' && echo "WARNING: metadata left, do not commit" >&2 || echo "No EXIF/GPS metadata left."
else
  magick identify -format '%wx%h px, EXIF tags: %[EXIF:*]\n' "$out"
fi
