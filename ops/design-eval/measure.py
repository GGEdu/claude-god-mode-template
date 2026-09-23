#!/usr/bin/env python3
"""Capturas + métricas de homogeneidad para una ronda de muestras (baseline/ o after/).

Uso: measure.py <dir_ronda>   → escribe <dir_ronda>/REPORT.md y <muestra>/shot-{desktop,mobile}.png
"""
import collections
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Fuentes que impeccable lista como "defaults de entrenamiento" (new-work.md §4) + Inter/Roboto/system.
OVERUSED_FONTS = {
    "inter", "roboto", "fraunces", "playfair display", "cormorant", "lora", "crimson",
    "newsreader", "syne", "space grotesk", "space mono", "ibm plex", "dm sans",
    "dm serif", "outfit", "plus jakarta sans", "instrument sans", "poppins", "montserrat",
}
GENERIC = {"sans-serif", "serif", "monospace", "system-ui", "-apple-system", "blinkmacsystemfont",
           "segoe ui", "helvetica", "arial", "inherit", "ui-sans-serif", "ui-monospace", "cursive"}

# Patrones del craft-floor de impeccable (heurísticos, sobre el HTML/CSS fuente).
PATTERNS = {
    "texto con degradado": r"background-clip:\s*text|-webkit-background-clip:\s*text",
    "eyebrow/kicker": r"class=\"[^\"]*(eyebrow|kicker|overline|pretitle|badge-top|section-label)",
    "border-left de acento": r"border-left:\s*[3-9]px",
    "glass/blur decorativo": r"backdrop-filter:\s*blur",
    "gradiente violeta/índigo": r"gradient\([^)]*#(6366f1|8b5cf6|7c3aed|a855f7|4f46e5|6d28d9)",
    "numeración 01/02/03": r">\s*0[1-3]\s*<",
    "grid de 3 tarjetas": r"repeat\(\s*3\s*,|grid-cols-3",
    "emoji como icono": r"[\U0001F300-\U0001FAFF]",
}


def fonts(html: str) -> list[str]:
    found = collections.Counter()
    for m in re.finditer(r"family=([^&\"':]+)", html):
        found[m.group(1).replace("+", " ").lower()] += 1
    for m in re.finditer(r"font-family:\s*([^;}\"]+)", html):
        first = m.group(1).split(",")[0].strip().strip("'\"").lower()
        if first.startswith("var("):
            continue
        found[first] += 1
    return [f for f, _ in found.most_common() if f not in GENERIC]


def colors(html: str, n: int = 6) -> list[str]:
    c = collections.Counter(h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", html))
    skip = {"#ffffff", "#000000"}
    return [h for h, _ in c.most_common(20) if h not in skip][:n]


IMPECCABLE = Path(__file__).resolve().parents[2] / "skills/impeccable/scripts/impeccable"


def detect(sample: Path) -> collections.Counter:
    env = {**os.environ, "IMPECCABLE_NO_TELEMETRY": "1", "IMPECCABLE_NO_UPDATE_CHECK": "1"}
    r = subprocess.run([str(IMPECCABLE), "detect", "--json", str(sample / "index.html")],
                       capture_output=True, text=True, env=env, timeout=120)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return collections.Counter({"detector-error": 1})
    items = data if isinstance(data, list) else data.get("findings", [])
    return collections.Counter(i.get("antipattern") or "?" for i in items)


def shoot(sample: Path) -> None:
    html = sample / "index.html"
    for name, size in (("desktop", "1440,2200"), ("mobile", "390,1800")):
        subprocess.run(
            ["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--window-size={size}", "--virtual-time-budget=4000",
             f"--screenshot={sample / f'shot-{name}.png'}", html.as_uri()],
            check=False, capture_output=True, timeout=60,
        )


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    rows, pattern_hits, all_fonts, det_total = [], collections.Counter(), collections.Counter(), collections.Counter()
    for sample in sorted(p for p in root.iterdir() if (p / "index.html").is_file()):
        html = (sample / "index.html").read_text(errors="replace")
        shoot(sample)
        fs = fonts(html)
        all_fonts.update(fs[:2])
        hits = [k for k, rx in PATTERNS.items() if re.search(rx, html, re.I)]
        pattern_hits.update(hits)
        det = detect(sample)
        det_total.update(det)
        over = [f for f in fs if any(f.startswith(o) for o in OVERUSED_FONTS)]
        rows.append(f"| {sample.name} | {', '.join(fs[:3]) or '—'} | {' '.join(colors(html))} "
                    f"| {', '.join(over) or '—'} | {', '.join(hits) or '—'} | {sum(det.values())} |")
    missing = [p.name for p in sorted(root.iterdir()) if p.is_dir() and not (p / "index.html").exists()]
    out = [f"# Métricas: {root.name}\n",
           "| Muestra | Fuentes | Colores dominantes | Fuentes sobreusadas | Patrones prohibidos | Detector impeccable |",
           "|---|---|---|---|---|---|", *rows,
           f"\n**Fuentes principales repetidas:** {dict(all_fonts.most_common())}",
           f"\n**Patrones prohibidos (nº de muestras):** {dict(pattern_hits.most_common())}",
           f"\n**Detector impeccable ({sum(det_total.values())} hallazgos):** {dict(det_total.most_common())}"]
    if missing:
        out.append(f"\n**Sin index.html:** {missing}")
    (root / "REPORT.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
