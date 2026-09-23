#!/usr/bin/env python3
"""Servidores MCP: una definición (mcp/servers.yaml) → formato de cada harness.

Subcomandos:
  import            crea mcp/servers.yaml desde lo instalado (~/.mcp.json, ~/.claude.json
                    y ~/.config/opencode/opencode.json). Rechaza secretos literales.
  render <harness>  imprime el bloque para claude (`mcpServers`) u opencode (`mcp`)
  diff [--json]     compara lo generado con lo instalado en cada harness

Las variables sensibles se guardan como referencia `{env: VAR}` y se escriben como
`${VAR}` (Claude) o `{env:VAR}` (opencode). Ningún subcomando imprime valores.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from catalog_lib import CATALOG, emit

HOME = Path.home()
SERVERS = CATALOG / "mcp/servers.yaml"
SOURCES = {"claude-project": HOME / ".mcp.json", "claude-user": HOME / ".claude.json",
           "opencode": HOME / ".config/opencode/opencode.json"}
SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASS|AUTH|COOKIE|CREDENTIAL", re.I)
CLAUDE_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
OPENCODE_REF = re.compile(r"\{env:([A-Za-z_][A-Za-z0-9_]*)\}")


class SecretError(Exception):
    pass


def looks_secret(value: str) -> bool:
    return bool(re.search(r"[A-Za-z0-9_\-]{32,}", value)) or "token=" in value.lower()


def to_value(name: str, raw, where: str):
    """Valor instalado → valor canónico: {env: VAR} o literal no secreto."""
    if not isinstance(raw, str):
        return raw
    m = CLAUDE_REF.fullmatch(raw) or OPENCODE_REF.fullmatch(raw)
    if m:
        return {"env": m.group(1)}
    if SECRET_NAME.search(name) or looks_secret(raw):
        raise SecretError(f"{where}.{name} tiene un valor literal que parece un secreto: "
                          "pásalo a variable de entorno antes de importar")
    return raw


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {}


def installed_claude() -> dict:
    servers = dict(load_json(SOURCES["claude-project"]).get("mcpServers") or {})
    servers.update(load_json(SOURCES["claude-user"]).get("mcpServers") or {})
    return servers


def installed_opencode() -> dict:
    return load_json(SOURCES["opencode"]).get("mcp") or {}


def canonical_from_claude(name: str, s: dict) -> dict:
    if s.get("type") in ("http", "sse") or s.get("url"):
        out = {"type": "http", "url": s["url"]}
        if s.get("headers"):
            out["headers"] = {k: to_value(k, v, name) for k, v in s["headers"].items()}
        return out
    args = s.get("args") or []
    for a in args:
        if isinstance(a, str) and looks_secret(a) and not CLAUDE_REF.search(a):
            raise SecretError(f"{name}: un argumento parece un secreto")
    out = {"type": "stdio", "command": s["command"], "args": args}
    if s.get("env"):
        out["env"] = {k: to_value(k, v, name) for k, v in s["env"].items()}
    return out


def canonical_env_from_opencode(name: str, s: dict) -> dict:
    return {k: to_value(k, v, name) for k, v in (s.get("environment") or {}).items()}


def cmd_import() -> int:
    claude, opencode = installed_claude(), installed_opencode()
    servers, notes = {}, []
    try:
        for name in sorted(set(claude) | set(opencode)):
            if name in claude:
                entry = canonical_from_claude(name, claude[name])
            else:
                s = opencode[name]
                cmd = s.get("command") or []
                entry = ({"type": "http", "url": s["url"]} if s.get("type") == "remote"
                         else {"type": "stdio", "command": cmd[0], "args": cmd[1:]})
                entry["harnesses"] = ["opencode"]
                notes.append(f"{name}: solo en opencode")
            if name in opencode and name in claude and entry["type"] == "stdio":
                oc_env = canonical_env_from_opencode(name, opencode[name])
                diff = {k: v for k, v in oc_env.items() if entry.get("env", {}).get(k) != v}
                if diff:
                    entry.setdefault("overrides", {})["opencode"] = {"env": diff}
                    notes.append(f"{name}: opencode difiere en {sorted(diff)}")
                oc_cmd = opencode[name].get("command") or []
                if oc_cmd != [entry["command"], *entry.get("args", [])]:
                    entry.setdefault("overrides", {}).setdefault("opencode", {})["command"] = oc_cmd
                    notes.append(f"{name}: opencode usa otro comando")
            elif name in opencode and entry["type"] == "stdio" and "harnesses" in entry:
                if opencode[name].get("environment"):
                    entry["env"] = canonical_env_from_opencode(name, opencode[name])
            servers[name] = entry
    except SecretError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    SERVERS.parent.mkdir(exist_ok=True)
    head = ("# Servidores MCP: definición única. `make mcp-diff` compara con lo instalado;\n"
            "# ops/mcp.py render claude|opencode genera cada formato. Sin secretos: los valores\n"
            "# sensibles son {env: VAR} y se resuelven del entorno (vault SOPS).\n")
    SERVERS.write_text(head + yaml.safe_dump({"servers": servers}, allow_unicode=True, sort_keys=False))
    print(f"✓ {SERVERS.relative_to(CATALOG)}: {len(servers)} servidores")
    for n in notes:
        print(f"  · {n}")
    return 0


def resolve(value, style: str):
    if isinstance(value, dict) and "env" in value:
        return f"${{{value['env']}}}" if style == "claude" else f"{{env:{value['env']}}}"
    return value


def servers_for(harness: str) -> dict:
    data = yaml.safe_load(SERVERS.read_text())["servers"]
    out = {}
    for name, s in data.items():
        if harness not in s.get("harnesses", ["claude", "opencode"]):
            continue
        env = {**(s.get("env") or {}), **((s.get("overrides") or {}).get(harness, {}).get("env") or {})}
        env = {k: resolve(v, harness) for k, v in env.items()}
        headers = {k: resolve(v, harness) for k, v in (s.get("headers") or {}).items()}
        if harness == "claude":
            if s["type"] == "http":
                out[name] = {"type": "http", "url": s["url"], **({"headers": headers} if headers else {})}
            else:
                out[name] = {"type": "stdio", "command": s["command"], "args": s.get("args") or [],
                             **({"env": env} if env else {})}
        else:
            if s["type"] == "http":
                out[name] = {"type": "remote", "url": s["url"], **({"headers": headers} if headers else {})}
            else:
                command = ((s.get("overrides") or {}).get(harness, {}).get("command")
                           or [s["command"], *(s.get("args") or [])])
                out[name] = {"type": "local", "command": command,
                             "enabled": True, **({"environment": env} if env else {})}
    return out


def normalize(harness: str, s: dict) -> dict:
    """Quita campos que el harness añade por defecto para comparar solo lo que importa."""
    s = {k: v for k, v in s.items() if v not in ({}, [], None)}
    if harness == "claude":
        s.setdefault("type", "stdio")
    else:
        s.setdefault("enabled", True)
    return s


def cmd_diff(as_json: bool) -> int:
    rows = []
    for harness, installed in (("claude", installed_claude()), ("opencode", installed_opencode())):
        wanted = servers_for(harness)
        for name in sorted(set(wanted) | set(installed)):
            if name not in installed:
                status = "falta"
            elif name not in wanted:
                status = "sobra"
            else:
                status = "igual" if normalize(harness, wanted[name]) == normalize(harness, installed[name]) else "difiere"
            rows.append({"harness": harness, "name": name, "status": status})
    problems = sum(1 for r in rows if r["status"] != "igual")

    def human(d):
        for r in d["items"]:
            if r["status"] != "igual":
                print(f"  {r['harness']:<9} {r['name']:<20} {r['status']}")
        print(f"{d['problems']} diferencias" if d["problems"] else "OK: MCP instalado = catálogo en ambos harness")
    emit({"problems": problems, "items": rows}, as_json, human)
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("import")
    r = sub.add_parser("render")
    r.add_argument("harness", choices=["claude", "opencode"])
    d = sub.add_parser("diff")
    d.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "import":
        return cmd_import()
    if a.cmd == "render":
        key = "mcpServers" if a.harness == "claude" else "mcp"
        json.dump({key: servers_for(a.harness)}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    return cmd_diff(a.json)


if __name__ == "__main__":
    sys.exit(main())
