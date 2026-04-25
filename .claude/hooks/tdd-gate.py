#!/usr/bin/env python3
"""TDD gate: verifica tests antes de escribir implementación (Sintesis.md §10.1).
   Configurable via settings.json hooks.tdd-gate section."""
import json, sys, os, fnmatch, glob, re

CONFIG_DEFAULTS = {
    "mode": "warn",
    # NEW-HIGH-9: patrones múltiples para cubrir tanto src/auth.ts (1 nivel)
    # como src/services/auth.ts (N niveles). fnmatch trata ** como *, así que
    # "src/**/*.ts" requiere ≥2 niveles. Añadidos patrones flat.
    "sourcePattern": [
        "src/*.{ts,py,rs,php,js,tsx,jsx,go,java,kt,rb,cs,swift,dart}",
        "src/**/*.{ts,py,rs,php,js,tsx,jsx,go,java,kt,rb,cs,swift,dart}",
        "app/*.{ts,py,php,rb}",
        "app/**/*.{ts,py,php,rb,jsx,tsx}",
        "lib/*.{ts,py,rs,php,rb,go,java,kt}",
        "lib/**/*.{ts,py,rs,php,rb,go,java,kt}",
    ],
    "testPattern": [
        "tests/**/*.test.{ts,py,php,js,rb,go}",
        "tests/**/*.spec.{ts,py,php,js,rb}",
        "test/**/*.{test,spec}.*",
        "spec/**/*.spec.*",
        "__tests__/**/*.{test,spec}.*",
        "*_test.{go,py}",
        "**/*_test.{go,py}",
    ],
    "excludePatterns": [
        "src/generated/**", "src/migrations/**",
        "**/generated/**", "**/migrations/**",
        "*.config.*", "*.d.ts",
        "**/__init__.py", "**/index.{ts,js}",
    ],
    "allowNewModules": True,
}


def load_config() -> dict:
    for path in [".claude/settings.json", ".claude/settings.local.json"]:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                cfg = data.get("hooks", {}).get("tdd-gate", {})
                if cfg:
                    return {**CONFIG_DEFAULTS, **cfg}
            except Exception:
                pass
    return CONFIG_DEFAULTS


def expand_brace(pattern: str) -> list[str]:
    m = re.search(r'\{([^}]+)\}', pattern)
    if not m:
        return [pattern]
    prefix, suffix = pattern[:m.start()], pattern[m.end():]
    return [p for opt in m.group(1).split(',') for p in expand_brace(prefix + opt + suffix)]


def matches_pattern(file_path: str, pattern_or_list) -> bool:
    patterns = []
    items = pattern_or_list if isinstance(pattern_or_list, list) else [pattern_or_list]
    for item in items:
        patterns.extend(expand_brace(item))
    return any(fnmatch.fnmatch(file_path, p) for p in patterns)


def find_test_file(source_path: str, test_pattern) -> str | None:
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    patterns = []
    items = test_pattern if isinstance(test_pattern, list) else [test_pattern]
    for item in items:
        patterns.extend(expand_brace(item))
    for tp in patterns:
        for match in glob.glob(tp, recursive=True):
            if base_name in os.path.basename(match):
                return match
    return None


def main():
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path", "")
    config = load_config()
    mode = config.get("mode", "warn")

    if mode == "off":
        json.dump({"decision": "allow", "reason": "tdd-gate desactivado (mode: off)"}, sys.stdout)
        sys.exit(0)

    for ep in config.get("excludePatterns", []):
        if matches_pattern(file_path, ep):
            json.dump({"decision": "allow", "reason": f"Excluido por patrón: {ep}"}, sys.stdout)
            sys.exit(0)

    if not matches_pattern(file_path, config.get("sourcePattern", "")):
        json.dump({"decision": "allow", "reason": "No es archivo de código fuente"}, sys.stdout)
        sys.exit(0)

    test_file = find_test_file(file_path, config.get("testPattern", ""))

    if test_file:
        json.dump({"decision": "allow", "reason": f"Test encontrado: {test_file}"}, sys.stdout)
        sys.exit(0)

    if mode == "block":
        json.dump({"decision": "block",
                   "reason": f"Tests requeridos antes de implementar {os.path.basename(file_path)}. Escribe el test primero."}, sys.stdout)
        sys.exit(1)

    if mode == "warn" or config.get("allowNewModules", True):
        msg = f"⚠️ TDD: Sin test para {os.path.basename(file_path)}. Considera escribir tests primero (RED→GREEN→REFACTOR)."
        json.dump({"decision": "allow", "reason": msg}, sys.stdout)
        sys.exit(0)

    json.dump({"decision": "block",
               "reason": f"Tests requeridos antes de implementar {os.path.basename(file_path)}. Escribe el test primero."}, sys.stdout)
    sys.exit(1)


if __name__ == "__main__":
    main()
