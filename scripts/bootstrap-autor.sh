#!/usr/bin/env bash
# bootstrap-autor.sh - prepares an AUTHOR's machine (macOS/Linux) to create/publish VEC skills.
#
# Usage:
#   # if you already cloned the repo, run it from inside:
#   bash scripts/bootstrap-autor.sh
#   # or standalone (it clones for you), if you have the script on hand:
#   bash bootstrap-autor.sh
#
# Idempotent. Does NOT grant Write access nor log git in — those need a human; it warns.

set -euo pipefail

REPO="${1:-rafaelnetovec/claude-skills}"
TARGET_DIR="${2:-$HOME/claude-skills}"

info() { printf '\033[36m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m[ok]\033[0m %s\n' "$1"; }
fail() { printf '  \033[31m[ERROR]\033[0m %s\n' "$1"; exit 1; }

info "== SkillHub - author bootstrap =="

# 1) prerequisites ----------------------------------------------------------
info $'\n1) Checking git and python3...'
command -v git >/dev/null 2>&1 || fail "git not found. Install it: 'xcode-select --install' (macOS) or 'brew install git'."
ok "git found"
command -v python3 >/dev/null 2>&1 || fail "python3 not found. Install Python 3.10+ (e.g. 'brew install python')."
PYVER="$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
PYMAJ="${PYVER%.*}"; PYMIN="${PYVER#*.}"
if [ "$PYMAJ" -lt 3 ] || { [ "$PYMAJ" -eq 3 ] && [ "$PYMIN" -lt 10 ]; }; then
  fail "Python $PYVER is too old. Need 3.10+."
fi
ok "python3 $PYVER"

# 2) locate or clone the repo ----------------------------------------------
info $'\n2) Locating the repository...'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
if [ -f "$REPO_ROOT/pyproject.toml" ] && [ -d "$REPO_ROOT/skills" ]; then
  ok "using the repo this script is in: $REPO_ROOT"
elif [ -d "$TARGET_DIR/.git" ]; then
  REPO_ROOT="$TARGET_DIR"
  ok "repo already cloned at $REPO_ROOT (updating)"
  git -C "$REPO_ROOT" pull --quiet
else
  info "  cloning $REPO into $TARGET_DIR ..."
  git clone "https://github.com/$REPO.git" "$TARGET_DIR" || fail "clone failed. Are you a collaborator (Write) and is git authenticated?"
  REPO_ROOT="$TARGET_DIR"
  ok "cloned at $REPO_ROOT"
fi
cd "$REPO_ROOT"

# 3) install the CLI --------------------------------------------------------
info $'\n3) Installing the SkillHub CLI...'
python3 -m pip install -e . --quiet || fail "failed to install the CLI. On macOS you may need a venv: 'python3 -m venv .venv && source .venv/bin/activate' then re-run."
ok "CLI installed"

# 4) test remote access (read + auth) --------------------------------------
info $'\n4) Testing access to the remote...'
git ls-remote origin >/dev/null 2>&1 || fail "no access to the remote. Accept the collaborator invite and check git auth."
ok "remote read/auth confirmed (write is validated on first publish)"

# 5) summary ----------------------------------------------------------------
info $'\n== Done! Current skills: =='
python3 -m skillhub.cli list
info $'\nNext steps (create and publish a skill):'
echo '  skill create my-skill --owner growth --description "What it does."'
echo '  skill validate my-skill'
echo '  skill bump my-skill minor'
echo '  skill publish my-skill --no-release'
echo
echo "If 'skill' is not found, use 'python3 -m skillhub.cli' instead."
