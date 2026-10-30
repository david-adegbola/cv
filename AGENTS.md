# Instructions for AI agents

Before you create or edit any CV in this repo, read [CV-RULES.md](CV-RULES.md) in full and
follow it. It has the workflow, layout, writing, honesty and privacy rules, and the canonical
facts every CV must agree with.

Never add AI-generated `Co-authored-by:` trailers to commits. Preserve legitimate human
co-authors. Run `./scripts/install-git-hooks.sh` to install the repository's shared
commit-message safeguard; it removes recognized AI-agent co-author trailers and chains any
existing `commit-msg` hook.
