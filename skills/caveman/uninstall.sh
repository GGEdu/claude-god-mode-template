#!/usr/bin/env bash
# Caveman uninstaller. Removes snippet block from any agent that has it.
# Block is delimited by <!-- CAVEMAN_ACTIVE --> ... <!-- /CAVEMAN_ACTIVE -->.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
AGENTS_DIR="$REPO_ROOT/agents"
START_MARKER="<!-- CAVEMAN_ACTIVE -->"
END_MARKER="<!-- /CAVEMAN_ACTIVE -->"

removed=0

for agent_file in "$AGENTS_DIR"/*.md; do
  [[ -f "$agent_file" ]] || continue
  if ! grep -qF "$START_MARKER" "$agent_file"; then
    continue
  fi
  # Remove the entire block (including markers).
  python3 - "$agent_file" "$START_MARKER" "$END_MARKER" <<'PY'
import sys, pathlib, re
path = pathlib.Path(sys.argv[1])
start, end = sys.argv[2], sys.argv[3]
text = path.read_text()
pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end) + r'\n*', re.DOTALL)
new = pattern.sub('', text).rstrip() + '\n'
path.write_text(new)
PY
  echo "  REMOVE $(basename "$agent_file" .md)"
  removed=$((removed + 1))
done

echo
echo "Removed Caveman from $removed agent(s)."
