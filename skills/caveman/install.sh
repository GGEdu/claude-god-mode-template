#!/usr/bin/env bash
# Caveman selective installer.
# Idempotent: re-running has no effect if already installed.
# Reversible: pair with uninstall.sh.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
SNIPPET_FILE="$SCRIPT_DIR/snippet.md"
AGENTS_DIR="$REPO_ROOT/agents"
MARKER="<!-- CAVEMAN_ACTIVE -->"

# Whitelist of agents that get Caveman.
# Reasoning: action-oriented output (diffs, fixes, status), not human-facing reasoning.
CAVEMAN_AGENTS=(
  "refactor-cleaner"
  "build-error-resolver"
  "cpp-build-resolver"
  "dart-build-resolver"
  "go-build-resolver"
  "java-build-resolver"
  "kotlin-build-resolver"
  "doc-updater"
  "e2e-runner"
  "memory-consolidator"
  "loop-operator"
)

# Explicitly excluded — must NOT receive Caveman.
# Reasoning: human-auditable reasoning, client-facing reports, nuanced judgments.
EXCLUDED_AGENTS=(
  "planner"
  "architect"
  "code-reviewer"
  "security-reviewer"
  "tdd-guide"
  "comment-analyzer"
  "conversation-analyzer"
  "harness-optimizer"
  "performance-optimizer"
  "pr-test-analyzer"
  "silent-failure-hunter"
  "ui-engineer"
  "database-reviewer"
  "docs-lookup"
  "github-orchestrator"
  "repo-reviewer"
  "cpp-reviewer"
  "csharp-reviewer"
  "flutter-reviewer"
  "go-reviewer"
  "java-reviewer"
  "kotlin-reviewer"
  "python-reviewer"
  "typescript-reviewer"
)

if [[ ! -f "$SNIPPET_FILE" ]]; then
  echo "ERROR: snippet.md not found at $SNIPPET_FILE" >&2
  exit 1
fi

if [[ ! -d "$AGENTS_DIR" ]]; then
  echo "ERROR: agents/ directory not found at $AGENTS_DIR" >&2
  exit 1
fi

installed=0
skipped_present=0
skipped_missing=0

for agent in "${CAVEMAN_AGENTS[@]}"; do
  agent_file="$AGENTS_DIR/${agent}.md"
  if [[ ! -f "$agent_file" ]]; then
    echo "  SKIP  $agent (file not found)"
    skipped_missing=$((skipped_missing + 1))
    continue
  fi
  if grep -qF "$MARKER" "$agent_file"; then
    echo "  SKIP  $agent (already installed)"
    skipped_present=$((skipped_present + 1))
    continue
  fi
  printf '\n\n' >> "$agent_file"
  cat "$SNIPPET_FILE" >> "$agent_file"
  echo "  ADD   $agent"
  installed=$((installed + 1))
done

# Sanity: no excluded agent should ever have the marker.
for agent in "${EXCLUDED_AGENTS[@]}"; do
  agent_file="$AGENTS_DIR/${agent}.md"
  if [[ -f "$agent_file" ]] && grep -qF "$MARKER" "$agent_file"; then
    echo "ERROR: excluded agent $agent has Caveman marker — manual cleanup required" >&2
    exit 2
  fi
done

echo
echo "Installed: $installed | Already present: $skipped_present | Missing files: $skipped_missing"
echo "Audit:    grep -l 'CAVEMAN_ACTIVE' $AGENTS_DIR/*.md"
