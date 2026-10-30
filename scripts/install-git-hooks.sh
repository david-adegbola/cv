#!/bin/sh
set -eu

repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "Run this script from inside a Git working tree." >&2
  exit 1
}
shared_hook=$repo_root/hooks/commit-msg
source_hooks_dir=$(git rev-parse --git-path hooks)
case $source_hooks_dir in
  /*) ;;
  *) source_hooks_dir=$repo_root/$source_hooks_dir ;;
esac

if [ ! -f "$shared_hook" ]; then
  echo "Shared commit-msg hook not found: $shared_hook" >&2
  exit 1
fi

git_dir=$(git rev-parse --absolute-git-dir)
hooks_dir=$git_dir/cv-hooks
source_marker=$hooks_dir/.source-hooks-dir

if [ "$source_hooks_dir" = "$hooks_dir" ]; then
  if [ ! -f "$source_marker" ]; then
    echo "Refusing to use $hooks_dir: it is not managed by this installer." >&2
    exit 1
  fi
  active_hook=$hooks_dir/commit-msg
  if [ -L "$active_hook" ] && [ "$(readlink "$active_hook")" = "$shared_hook" ]; then
    echo "Repository commit-msg hook is already installed."
    exit 0
  fi
  echo "Managed commit-msg hook is missing or has been changed: $active_hook" >&2
  exit 1
fi

if [ -e "$hooks_dir" ]; then
  echo "Refusing to replace existing hooks directory: $hooks_dir" >&2
  exit 1
fi

mkdir "$hooks_dir"
printf '%s\n' "$source_hooks_dir" >"$source_marker"

for source_hook in "$source_hooks_dir"/*; do
  [ -f "$source_hook" ] && [ -x "$source_hook" ] || continue
  hook_name=$(basename "$source_hook")
  if [ "$hook_name" = commit-msg ]; then
    hook_name=commit-msg.pre-ai-trailer
  fi
  ln -s "$source_hook" "$hooks_dir/$hook_name"
done

ln -s "$shared_hook" "$hooks_dir/commit-msg"
git config --local core.hooksPath "$hooks_dir"

if [ "$(git rev-parse --git-path hooks)" = "$hooks_dir" ]; then
  echo "Installed repository hooks in $hooks_dir and preserved existing hooks from $source_hooks_dir."
else
  echo "Failed to activate repository hooks in $hooks_dir." >&2
  exit 1
fi
