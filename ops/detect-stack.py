#!/usr/bin/env python3
"""
Auto-detect the best stack for a project by scanning its files.

Usage:
    python3 ops/detect-stack.py <project_path> [stacks_dir]

Scans the project for language markers (package.json, composer.json, go.mod, etc.)
and scores each available stack. Prints the best match with confidence.

Exit codes:
    0 — stack detected, name printed to stdout
    1 — no match found or error
"""

import json
import os
import sys

import yaml


# Markers: (file_or_dir, content_pattern, stack_scores)
# Each marker contributes points to one or more stacks.
MARKERS = [
    # Go
    ("go.mod", None, {"go-api": 10}),
    ("go.sum", None, {"go-api": 5}),
    # Laravel + PHP
    ("composer.json", "laravel/framework", {"laravel-react": 10}),
    ("composer.json", None, {"laravel-react": 3, "odoo": -2}),
    ("artisan", None, {"laravel-react": 8}),
    # React / Frontend JS
    ("package.json", '"react"', {"laravel-react": 5, "nextjs-saas": 3}),
    ("package.json", '"next"', {"nextjs-saas": 10, "laravel-react": -3}),
    ("package.json", '"vue"', {"laravel-react": -2, "nextjs-saas": -2}),
    # Supabase
    ("supabase/", None, {"nextjs-saas": 5}),
    (".env", "SUPABASE", {"nextjs-saas": 4}),
    # Python general
    ("requirements.txt", None, {"python-api": 5, "odoo": 3}),
    ("pyproject.toml", None, {"python-api": 5, "odoo": 2}),
    ("manage.py", None, {"python-api": 8}),
    # Django
    ("requirements.txt", "django", {"python-api": 10}),
    ("pyproject.toml", "django", {"python-api": 10}),
    # FastAPI
    ("requirements.txt", "fastapi", {"python-api": 10}),
    ("pyproject.toml", "fastapi", {"python-api": 10}),
    # Odoo
    ("__manifest__.py", None, {"odoo": 15}),
    ("odoo/", None, {"odoo": 10}),
    ("requirements.txt", "odoo", {"odoo": 12}),
    # Stripe (SaaS indicator)
    ("package.json", "stripe", {"nextjs-saas": 4}),
    (".env", "STRIPE", {"nextjs-saas": 3}),
    # Sanctum (Laravel auth)
    ("composer.json", "sanctum", {"laravel-react": 4}),
    # MySQL vs PostgreSQL
    (".env", "DB_CONNECTION=mysql", {"laravel-react": 2}),
    (".env", "DATABASE_URL.*postgres", {"python-api": 2, "nextjs-saas": 2, "go-api": 2}),
]


def file_contains(filepath, pattern):
    """Check if a file contains a pattern (case-insensitive)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
        return pattern.lower() in content
    except (OSError, UnicodeDecodeError):
        return False


def detect_stack(project_path, stacks_dir):
    """Score each stack based on project markers."""
    # Load available stacks
    available_stacks = {}
    for entry in sorted(os.listdir(stacks_dir)):
        stack_yaml = os.path.join(stacks_dir, entry, "stack.yaml")
        if os.path.isfile(stack_yaml):
            with open(stack_yaml, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            available_stacks[entry] = {
                "description": data.get("description", ""),
                "score": 0,
                "matches": [],
            }

    if not available_stacks:
        return None, {}

    # Score markers
    for marker_path, content_pattern, scores in MARKERS:
        full_path = os.path.join(project_path, marker_path)

        # Check if file/dir exists
        exists = os.path.exists(full_path)
        if not exists:
            continue

        # If content pattern specified, check file content
        if content_pattern and os.path.isfile(full_path):
            if not file_contains(full_path, content_pattern):
                continue

        # Apply scores
        marker_desc = marker_path
        if content_pattern:
            marker_desc += f" (contains '{content_pattern}')"

        for stack_name, points in scores.items():
            if stack_name in available_stacks:
                available_stacks[stack_name]["score"] += points
                if points > 0:
                    available_stacks[stack_name]["matches"].append(
                        f"+{points} {marker_desc}"
                    )

    # Find best match
    ranked = sorted(
        available_stacks.items(), key=lambda x: x[1]["score"], reverse=True
    )
    best_name, best_data = ranked[0]

    if best_data["score"] <= 0:
        return None, available_stacks

    return best_name, available_stacks


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project_path> [stacks_dir]", file=sys.stderr)
        sys.exit(1)

    project_path = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stacks_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(script_dir, "..", "stacks")
    stacks_dir = os.path.abspath(stacks_dir)

    if not os.path.isdir(project_path):
        print(f"❌ Project directory not found: {project_path}", file=sys.stderr)
        sys.exit(1)

    best, all_stacks = detect_stack(project_path, stacks_dir)

    # JSON mode for programmatic use
    if "--json" in sys.argv:
        result = {
            "detected": best,
            "scores": {k: v["score"] for k, v in all_stacks.items()},
        }
        print(json.dumps(result))
        sys.exit(0 if best else 1)

    # Human-readable output
    if best:
        print(f"🔍 Stack detectado: {best}")
        print(f"   {all_stacks[best]['description']}")
        print(f"   Score: {all_stacks[best]['score']}")
        print()
        if all_stacks[best]["matches"]:
            print("   Evidencia:")
            for m in all_stacks[best]["matches"]:
                print(f"     {m}")
        print()
        # Print ranking
        ranked = sorted(all_stacks.items(), key=lambda x: x[1]["score"], reverse=True)
        if len(ranked) > 1 and ranked[1][1]["score"] > 0:
            print("   Alternativas:")
            for name, data in ranked[1:]:
                if data["score"] > 0:
                    print(f"     {name}: score {data['score']}")
    else:
        print("❌ No se pudo detectar el stack del proyecto.", file=sys.stderr)
        print("   Usa: make list-stacks  para ver opciones disponibles", file=sys.stderr)
        sys.exit(1)

    # Print just the stack name on the last line for easy parsing
    print(f"\nSTACK={best}")


if __name__ == "__main__":
    main()
