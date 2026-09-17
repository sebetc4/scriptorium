#!/usr/bin/env python3
"""Propagate the art direction from brand/tokens.yaml to its two consumers.

  1. brand/tokens.css                        -> read by the theme/*.css sheets (PDF)
  2. ~/.diagram-design/profiles/<slug>.md    -> read by the diagram-design skill
     + <root>/.diagram-design                -> the marker selecting that profile

diagram-design is NEVER modified: it is a plugin installed outside the
repository and replaced on every update. Everything goes through the profile
mechanism it provides, which survives those updates.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "brand" / "tokens.yaml"
OUT_CSS = ROOT / "brand" / "tokens.css"
PROFILES = Path.home() / ".diagram-design" / "profiles"
MARKER = ROOT / ".diagram-design"
SLUG = "scriptorium"

# diagram-design is installed as a plugin: its path depends on the version and
# lives outside the repository. It is resolved at run time rather than fixed.
PLUGIN_ROOT = Path.home() / ".claude" / "plugins"
GUIDE_REL = Path("skills") / "diagram-design" / "references" / "style-guide.md"


def _version_key(path: Path) -> tuple:
    """Sorts 2.6.22 after 2.6.9 — a lexical sort would do the opposite."""
    parts = re.findall(r"\d+", path.name)
    return (len(parts) > 0, [int(n) for n in parts], path.name)


def find_dd_guide() -> Path | None:
    """Locate the style guide of the installed diagram-design skill.

    In order: the variable Claude Code sets when the script runs from a plugin,
    the install declared for this repository, then the most recent version in
    the cache.
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        guide = Path(env) / GUIDE_REL
        if guide.exists():
            return guide

    registry = PLUGIN_ROOT / "installed_plugins.json"
    if registry.exists():
        try:
            installs = json.loads(registry.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            installs = {}
        for entry in installs.get("plugins", {}).get("diagram-design@diagram-design", []):
            if Path(entry.get("projectPath", "")) != ROOT:
                continue
            guide = Path(entry.get("installPath", "")) / GUIDE_REL
            if guide.exists():
                return guide

    cache = PLUGIN_ROOT / "cache" / "diagram-design" / "diagram-design"
    if cache.is_dir():
        for version in sorted(cache.iterdir(), key=_version_key, reverse=True):
            guide = version / GUIDE_REL
            if guide.exists():
                return guide

    return None


# diagram-design role -> tokens.yaml key (1:1, hence the shared art direction)
ROLES = ["paper", "paper-2", "ink", "muted", "soft", "rule",
         "rule-solid", "accent", "accent-tint", "link"]

# Roles specific to the PDFs. They are not propagated to diagram-design, whose
# model holds to a single accented tint: adding roles it does not know would
# only invite breaking its own rule.
PDF_ONLY = ["alert", "alert-tint", "danger", "danger-tint"]


def load() -> dict:
    if not TOKENS.exists():
        sys.exit(f"not found: {TOKENS}")
    return yaml.safe_load(TOKENS.read_text(encoding="utf-8"))


def first_family(stack: str) -> str:
    """'Noto Serif', Georgia, serif  ->  Noto Serif"""
    return stack.split(",")[0].strip().strip("'\"")


# --------------------------------------------------------------------------
# Resolving the palette references
# --------------------------------------------------------------------------
ALPHA_RE = re.compile(r"alpha\(\s*([\w.\-]+)\s*,\s*([01]?\.?\d*)\s*\)")


def lookup(path: str, palette: dict, where: str) -> str:
    node = palette
    for seg in path.split("."):
        key = int(seg) if seg.isdigit() else seg
        if not isinstance(node, dict) or key not in node:
            sys.exit(f"{where}: palette path not found “{path}”")
        node = node[key]
    if not isinstance(node, str) or not node.startswith("#"):
        sys.exit(f"{where}: “{path}” does not name a colour")
    return node


def resolve(value, palette: dict, where: str) -> str:
    """hex | literal rgba() | a path into `palette` | alpha(path, opacity)"""
    v = str(value).strip()
    if v == "transparent" or v.startswith(("#", "rgb(", "rgba(")):
        return v
    m = ALPHA_RE.fullmatch(v)
    if m:
        h = lookup(m.group(1), palette, where).lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{m.group(2)})"
    return lookup(v, palette, where)


def resolved(t: dict) -> dict:
    """{'light': {role: hex/rgba}, 'dark': {...}} — every reference resolved."""
    palette = t.get("palette") or {}
    out: dict[str, dict[str, str]] = {}
    for mode in ("light", "dark", "epub"):
        src = t["colors"][mode]
        missing = [r for r in ROLES + PDF_ONLY if r not in src]
        if missing:
            sys.exit(f"colors.{mode}: missing roles — {', '.join(missing)}")
        out[mode] = {r: resolve(src[r], palette, f"colors.{mode}.{r}")
                     for r in ROLES + PDF_ONLY}
    return out


# --------------------------------------------------------------------------
# 1. CSS
# --------------------------------------------------------------------------
def emit_css(t: dict, colors: dict) -> None:
    ty, pg, br = t["type"], t["page"], t["brand"]
    ic = t.get("icon") or {}
    lines = [
        "/* GENERATED BY brand/sync.py — DO NOT EDIT BY HAND.",
        "   Edit brand/tokens.yaml, then run `make brand` again. */",
        "",
    ]
    for face in ty.get("faces") or []:
        src = ROOT / "brand" / "fonts" / face["file"]
        if not src.exists():
            print(f"  ! font declared but missing: brand/fonts/{face['file']}")
            continue
        lines += [
            "@font-face {",
            f"  font-family: '{face['family']}';",
            f"  src: url('fonts/{face['file']}');",
            f"  font-weight: {face.get('weight', 400)};",
            f"  font-style: {face.get('style', 'normal')};",
            "}",
        ]
    if len(lines) > 3:
        lines.append("")
    lines.append(":root {")
    for role in ROLES + PDF_ONLY:
        lines.append(f"  --{role}: {colors['light'][role]};")
    lines.append("")
    for name in ("serif", "sans", "mono"):
        lines.append(f"  --font-{name}: {ty[name]};")
    lines += [
        f"  --font-body: var(--font-{ty['body']});",
        f"  --font-head: var(--font-{ty['head']});",
        "",
        f"  --size: {ty['size']};",
        f"  --lead: {ty['lead']};",
        f"  --scale: {ty['scale']};",
        "",
        f"  --page-size: {pg['size']};",
        f"  --page-margin: {pg['margin']};",
        f"  --measure: {pg['measure']};",
        f"  --cover-height: {pg['cover-height']};",
        f"  --figure-max-height: {pg['figure-max-height']};",
        f"  --radius: {br['radius']};",
        "",
        f"  --icon-stroke: {ic.get('stroke', 2)};",
        f"  --icon-size: {ic.get('size', '1em')};",
        "}",
        "",
        "/* Dark variant: reserved for the documents that ask for it",
        "   explicitly, through `theme: dark` in their front matter. */",
        '[data-theme="dark"] {',
    ]
    for role in ROLES + PDF_ONLY:
        lines.append(f"  --{role}: {colors['dark'][role]};")
    lines += [
        "}",
        "",
        "/* EPUB output: roles at equalised luminance, tinted backgrounds",
        "   removed. Read by the epub skill's epub.py, which flattens the sheet before",
        "   embedding it — an e-reader does not resolve var(). */",
        '[data-theme="epub"] {',
    ]
    for role in ROLES + PDF_ONLY:
        lines.append(f"  --{role}: {colors['epub'][role]};")
    lines += ["}", ""]
    OUT_CSS.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {OUT_CSS.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# 2. The diagram-design profile
# --------------------------------------------------------------------------
def emit_profile(t: dict, colors: dict) -> None:
    guide = find_dd_guide()
    if guide is None:
        print("  · diagram-design missing — profile not generated")
        return

    pristine = guide.read_text(encoding="utf-8")
    if pristine.lstrip().startswith("<!-- diagram-design-profile"):
        print("  ! the installed copy already carries a profile header; "
              "generation skipped so a derived art direction is not propagated")
        return

    PROFILES.mkdir(parents=True, exist_ok=True)
    # The recovery backup references/profiles.md requires, before anything else.
    default = PROFILES / "default.md"
    if not default.exists():
        today = dt.date.today().isoformat()
        default.write_text(
            "<!-- diagram-design-profile\n"
            "name: Default\nslug: default\nsource-url: none\n"
            f"created: {today}\nupdated: {today}\n"
            "notes: Pristine shipped style guide\n-->\n" + pristine,
            encoding="utf-8")
        print(f"  ✓ {default} (recovery backup)")

    body = pristine
    light, dark = colors["light"], colors["dark"]
    for role in ROLES:
        # | `role` | usage | light | dark |  -> only the 2 values are replaced
        pat = re.compile(
            rf"^(\|\s*`{re.escape(role)}`\s*\|[^|]*\|)[^|]*\|[^|]*\|(.*)$", re.M)
        new, n = pat.subn(
            lambda m: f"{m.group(1)} `{light[role]}` | `{dark[role]}` |{m.group(2)}",
            body)
        if n:
            body = new
        else:
            print(f"  ! role absent from the diagram-design schema: {role}")

    body = re.sub(
        r"^> \*\*Brand palette source:\*\*.*$",
        "> **Brand palette source:** generated from `brand/tokens.yaml` in the "
        "scriptorium repository, which is the single source of truth for this "
        "skin. Edit that file and run `make brand` — never edit this profile by "
        "hand. `rule` and the tint tokens are ink/accent at opacity; roles the "
        "brand palette does not name directly are listed under its `derived` "
        "group.",
        body, count=1, flags=re.M)

    fam = {"title": first_family(t["type"]["serif"]),
           "callout": first_family(t["type"]["serif"]),
           "node-name": first_family(t["type"]["sans"]),
           "sublabel": first_family(t["type"]["mono"]),
           "eyebrow": first_family(t["type"]["mono"]),
           "arrow-label": first_family(t["type"]["mono"])}
    for role, family in fam.items():
        pat = re.compile(rf"^(\|\s*`{re.escape(role)}`\s*\|)[^|]*\|", re.M)
        body = pat.sub(lambda m: f"{m.group(1)} {family} |", body)

    today = dt.date.today().isoformat()
    created = today
    target = PROFILES / f"{SLUG}.md"
    if target.exists():  # the creation date is preserved
        m = re.search(r"^created:\s*(\S+)", target.read_text(encoding="utf-8"), re.M)
        if m:
            created = m.group(1)

    header = ("<!-- diagram-design-profile\n"
              f"name: {str(t['name']).replace('--', '-')}\n"
              f"slug: {SLUG}\nsource-url: none\n"
              f"created: {created}\nupdated: {today}\n"
              "notes: Generated from brand/tokens.yaml — do not edit by hand\n"
              "-->\n")
    target.write_text(header + body, encoding="utf-8")
    MARKER.write_text(f"profile: {SLUG}\n", encoding="utf-8")
    print(f"  ✓ {target}")
    print(f"  ✓ {MARKER.relative_to(ROOT)} (profile: {SLUG})")


def main() -> None:
    t = load()
    colors = resolved(t)
    print(f"art direction “{t['name'] }”:")
    emit_css(t, colors)
    emit_profile(t, colors)


if __name__ == "__main__":
    main()
