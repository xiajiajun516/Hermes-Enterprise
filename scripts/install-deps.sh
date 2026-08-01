#!/usr/bin/env bash
# Hermes Enterprise — dependency checker / installer (idempotent).
#
# Verifies git, node, npm, python, semgrep, and the ocr CLI
# (alibaba/open-code-review). Installs semgrep (pip) and ocr (npm); the rest
# are reported with install hints (git/node/python are system-level installs
# better done by the user's own package manager). Safe to re-run at any time.
set -euo pipefail

ok()   { echo "OK   $1"; }
fail() { echo "FAIL $1"; }

echo "==> Hermes Enterprise dependency check"

# --- git (>= 2.41 required by ocr) -------------------------------------------
if command -v git >/dev/null 2>&1; then
  ok "git: $(git --version)"
else
  fail "git: not found — install Git >= 2.41 first (https://git-scm.com/)"
  exit 1
fi

# --- node / npm --------------------------------------------------------------
if command -v node >/dev/null 2>&1; then
  ok "node: $(node --version)"
else
  fail "node: not found — install Node.js >= 18 (https://nodejs.org/)"
  exit 1
fi
if command -v npm >/dev/null 2>&1; then
  ok "npm: $(npm --version)"
else
  fail "npm: not found (ships with Node.js)"
  exit 1
fi

# --- python (>= 3.11 for scripts/sync_skills.py) -----------------------------
# Note: on Windows, a bare `python3` may hit the Microsoft Store alias stub
# (exit != 0 / empty output) — fall back to `python` in that case.
if PYVER=$(python3 --version 2>/dev/null); then
  ok "python3: $PYVER"
elif PYVER=$(python --version 2>/dev/null); then
  ok "python: $PYVER"
else
  fail "python: not found — install Python >= 3.11 (https://python.org/)"
  exit 1
fi

# --- semgrep (deterministic zero-token scan layer for the QA gate) ------------
if command -v semgrep >/dev/null 2>&1; then
  ok "semgrep: $(semgrep --version)"
else
  echo "==> installing semgrep (pip)..."
  if ! (python -m pip install semgrep 2>/dev/null || pip install semgrep 2>/dev/null); then
    fail "semgrep: pip install failed — install manually (https://semgrep.dev/docs/getting-started/)"
    exit 1
  fi
  ok "semgrep installed: $(semgrep --version)"
fi

# --- ocr CLI (optional but recommended for the QA gate) -----------------------
if command -v ocr >/dev/null 2>&1; then
  ok "ocr: $(ocr --version 2>/dev/null | head -1)"
else
  echo "==> installing ocr (alibaba/open-code-review)..."
  npm install -g @alibaba-group/open-code-review
  ok "ocr installed: $(ocr --version 2>/dev/null | head -1)"
fi

echo "==> All dependencies satisfied."
echo "    Note: ocr can run in delegation mode (no LLM config) — see README."
