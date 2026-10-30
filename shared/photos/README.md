# Profile photos

Placeholder: add your photo here as `david.jpg`. No photo is committed yet, and no CV uses one.

Before committing a photo, strip its metadata (EXIF, GPS location, camera details) and resize it to at most 600×600 px:

```bash
shared/photos/prepare-photo.sh ~/Pictures/my-photo.jpg   # writes shared/photos/david.jpg
```

A square, head-and-shoulders photo works best. It is cropped to a circle and anything outside the centre is cut off.

This repo is public: once a photo is pushed it stays in the git history, even if you delete it later. The build workflow also strips and resizes photos before compiling, but that only protects the PDFs, not the repo.
