"""Constantes compartidas para hooks de la state machine (Sintesis.md §2).

CONT-9 fix: centraliza paths y patrones para que plan-gate, non-goal-guard, etc.
no diverjan en su universo de archivos.
"""
from pathlib import Path

PROJECT_ROOT = Path.cwd()

PLAN_LOCATIONS: list[str] = [
    ".claude/plans/PLAN.md",
    "PLAN.md",
]

STATE_PATH: str = ".claude/state.yaml"
SESSION_READS_LOG: str = ".claude/session-reads.log"
HOOK_HEALTH_LOG: str = ".claude/memory/hook-health.log"
PLAN_DRIFT_LOG: str = ".claude/memory/plan-drift.log"
COMMIT_BYPASS_LOG: str = ".claude/memory/commit-bypass.log"
LESSONS_DIR: str = ".claude/memory/lessons"
LESSONS_INDEX: str = ".claude/memory/lessons/_index.yaml"

META_WHITELIST: list[str] = [
    "PLAN.md", "PLAN.v*.md", "RESEARCH.md", "VERIFICATION.md",
    "REVIEW.md", "SECURITY.md",
    "**/PLAN.md", "**/PLAN.v*.md", "**/RESEARCH.md", "**/VERIFICATION.md",
    "**/REVIEW.md", "**/SECURITY.md",
    ".claude/memory/**", "docs/src/wiki/**",
    "**/*.log", "**/*.yaml", "**/*.yml",
    ".claude/hooks/**", ".claude/plans/**", ".claude/commands/**",
    ".gitignore", "**/.gitkeep", "**/.gitignore",
]

SENSITIVE_PATTERNS: list[str] = [
    "**/auth/**", "**/security/**", "**/payment*/**",
    "**/admin/**", "**/secrets/**", "**/credentials/**",
]

FAST_PATH_MAX_FILES: int = 3
FAST_PATH_MAX_LINES: int = 50

HOOK_TIMEOUT_SECONDS: int = 10
GIT_TIMEOUT_SECONDS: int = 5

PLAN_REQUIRED_FIELDS: list[str] = [
    "plan_id",
    "files_affected",
    "acceptance_criteria",
]

VALID_STATES: list[str] = [
    "INIT", "EXPLORE", "PLAN", "EXECUTE",
    "VERIFY", "DONE", "BLOCKED", "RE-PLAN", "FAST_PATH",
]
