#!/usr/bin/env bash
# Push without Cursor's GIT_ASKPASS (avoids 401 from broken askpass).
# Requires a one-line Git credential store (see message below).
set -euo pipefail
cd "$(dirname "$0")"
CRED="${HOME}/.config/git/credentials-jebat8101-github"
if [[ ! -s "$CRED" ]] || ! grep -q 'github\.com' "$CRED" 2>/dev/null; then
  echo "Missing PAT file: $CRED"
  echo "Create it with one line (use your real PAT from github.com/settings/tokens):"
  echo "  printf '%s\\n' 'https://jebat8101:YOUR_PAT_HERE@github.com' > \"$CRED\" && chmod 600 \"$CRED\""
  exit 1
fi
unset GIT_ASKPASS SSH_ASKPASS
export GIT_TERMINAL_PROMPT=0
exec git push -u origin main "$@"
