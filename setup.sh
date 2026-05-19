#!/usr/bin/env bash
# Querious — setup tanpa torch/CUDA (jimat disk)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

VENV_DIR="${VENV_DIR:-$ROOT/.venv}"

echo "==> Querious: install semua tool (ringan, tanpa PyTorch/CUDA)"
echo "    Root: $ROOT"

# Kosongkan cache pip jika disk penuh dari percubaan lepas
if df -h . | tail -1 | grep -qE '100%|9[0-9]%'; then
  echo "==> AMARAN: disk hampir penuh — cuba pip cache purge"
  pip cache purge 2>/dev/null || true
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "==> Cipta virtualenv: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "==> Upgrade pip"
pip install --upgrade pip wheel setuptools

echo "==> pip install -r requirements.txt"
pip install -r requirements.txt

if [[ -f "$ROOT/OSINT/ghunt/pyproject.toml" ]]; then
  echo "==> GHunt (editable)"
  pip install -e "$ROOT/OSINT/ghunt"
fi

if [[ -f "$ROOT/OSINT/sherlock/pyproject.toml" ]]; then
  echo "==> Sherlock (editable)"
  pip install -e "$ROOT/OSINT/sherlock"
fi

echo ""
echo "==> Selesai (core OSINT tools)."
echo "    ML berat (torch): pip install -r requirements-optional.txt  # ~2GB+, pilihan"
echo ""
echo "  source $VENV_DIR/bin/activate"
echo "  streamlit run main.py"
echo ""
