"""Generate ROADMAP.md from course.yml.

Usage:
  python scripts/build_roadmap.py          # write ROADMAP.md
  python scripts/build_roadmap.py --check  # fail if ROADMAP.md is out of date
"""

from __future__ import annotations

import sys

from course import ROOT, load_course

OUT = ROOT / "ROADMAP.md"


def render() -> str:
    c = load_course()
    total = len(c.lessons)
    done = sum(l.done for l in c.lessons)

    lines = [
        "# Learning Roadmap",
        "",
        "<!-- This file is generated from course.yml. Do not edit by hand.",
        "     Change course.yml, then run: python scripts/build_roadmap.py -->",
        "",
        f"**Progress: {done} / {total} lessons published**",
        "",
        "✅ = published · ⬜ = coming soon",
        "",
        "---",
        "",
    ]

    active = [p for p in c.phases if not p.planned]
    planned = [p for p in c.phases if p.planned]

    for p in active:
        lines.append(f"## {p.id} — {p.title}")
        lines.append("")
        for m in p.modules:
            lines.append(f"### {m.title}")
            for l in m.lessons:
                if l.done:
                    lines.append(f"- ✅ [{l.title}]({l.rel_path})")
                else:
                    lines.append(f"- ⬜ {l.title}")
            lines.append("")

    if planned:
        lines += ["---", "", "## Planned phases", ""]
        for p in planned:
            lines.append(f"### {p.id} — {p.title}")
            if p.summary:
                lines.append(p.summary)
            if p.note:
                lines += ["", f"> {p.note}"]
            lines.append("")

    if c.project_ideas:
        lines += ["---", "", "## Project ideas", "",
                  "Community projects live in [`projects/`](projects/). Some ideas to start:", ""]
        for i, idea in enumerate(c.project_ideas, 1):
            lines.append(f"{i}. {idea}")
        lines += ["", "Have your own idea? Add it through a pull request — see [CONTRIBUTING.md](CONTRIBUTING.md).", ""]

    return "\n".join(lines)


def main() -> int:
    text = render()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("ROADMAP.md is out of date. Run: python scripts/build_roadmap.py")
            return 1
        print("ROADMAP.md is up to date.")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
