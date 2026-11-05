"""Check lessons, projects and the roadmap.

Usage:
  python scripts/validate.py                    # check everything
  python scripts/validate.py --base <git-sha>   # in CI: skip if the PR doesn't touch course files
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

import build_roadmap
from course import (
    LESSON_ALLOWED,
    LESSON_REQUIRED,
    LESSONS_DIR,
    PROJECT_REQUIRED,
    PROJECTS_DIR,
    ROOT,
    SLUG_RE,
    headings,
    load_course,
)

WATCHED = ("lessons/", "projects/", "course.yml", "ROADMAP.md")
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_FILE_MB = 5

SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "a private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "a GitHub token"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"), "a Slack token"),
    (re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"), "an API secret key"),
]

TEMPLATE_LEFTOVERS = [
    "https://example.com",
    "(1–2 lines)",
    "@your-github-username",
    "# command — what it does",
]

errors: list[tuple[str, str]] = []  # (file, message)


def err(file: Path | str, msg: str) -> None:
    rel = str(Path(file).relative_to(ROOT)) if isinstance(file, Path) and Path(file).is_absolute() else str(file)
    errors.append((rel, msg))


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# ───────────────────────── helpers ─────────────────────────

def changed_files(base: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return [l for l in out.splitlines() if l.strip()]


def section_body(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def check_links(path: Path, text: str) -> None:
    """Relative links and images inside a markdown file must point to real files."""
    no_code = re.sub(r"```.*?```", "", text, flags=re.S)
    for target in re.findall(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", no_code):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        clean = target.split("#")[0]
        if not clean:
            continue
        if not (path.parent / clean).resolve().exists():
            err(path, f"broken link: '{target}' does not exist")


def check_secrets(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    for pattern, what in SECRET_PATTERNS:
        if pattern.search(text):
            err(path, f"looks like it contains {what}. Remove it — never commit secrets.")


def check_leftovers(path: Path, text: str) -> None:
    for t in TEMPLATE_LEFTOVERS:
        if t in text:
            err(path, f"template placeholder left in file: '{t}'")


# ───────────────────────── lessons ─────────────────────────

def check_lesson_file(lesson, text: str) -> None:
    path = lesson.path
    lines = text.lstrip("﻿").splitlines()

    if not lines or not lines[0].startswith("# "):
        err(path, "first line must be the lesson title, like '# What is an IP address?'")

    if "> **Phase:**" not in text or "> **Module:**" not in text:
        err(path, "missing the info block at the top ('> **Phase:** ...' and '> **Module:** ...'). Copy it from LESSON_TEMPLATE.md")

    found = headings(text)
    for h in LESSON_REQUIRED:
        if h not in found:
            err(path, f"missing required section '## {h}'")
        elif not section_body(text, h):
            err(path, f"section '## {h}' is empty")

    unknown = [h for h in found if h not in LESSON_ALLOWED]
    for h in unknown:
        close = difflib.get_close_matches(h, LESSON_ALLOWED, n=1)
        hint = f" — did you mean '## {close[0]}'?" if close else f". Allowed: {', '.join(LESSON_ALLOWED)}"
        err(path, f"unknown section '## {h}'{hint}")

    known = [h for h in found if h in LESSON_ALLOWED]
    if known != sorted(known, key=LESSON_ALLOWED.index):
        err(path, "sections are in the wrong order. Follow the order in LESSON_TEMPLATE.md")
    if len(known) != len(set(known)):
        err(path, "a section heading is used twice")

    refs = section_body(text, "References")
    if refs and not re.search(r"https?://", refs):
        err(path, "'## References' needs at least one link to a real source")

    check_leftovers(path, text)
    check_links(path, text)


def check_lessons(course) -> None:
    lessons_by_path = {l.rel_path: l for l in course.lessons}
    phases = {p.dirname: p for p in course.phases}

    if not LESSONS_DIR.is_dir():
        return

    for f in sorted(LESSONS_DIR.rglob("*")):
        if f.is_dir():
            continue
        r = rel(f)
        parts = Path(r).parts  # ('lessons', phase, module, file...)

        if f.name == ".gitkeep":
            continue
        if f.stat().st_size > MAX_FILE_MB * 1024 * 1024:
            err(f, f"file is bigger than {MAX_FILE_MB} MB")
        check_secrets(f)

        if r == "lessons/README.md":
            continue

        # phase folder
        if len(parts) < 3:
            err(f, "files must go inside a phase folder, e.g. lessons/01-networking-fundamentals/")
            continue
        phase = phases.get(parts[1])
        if not phase:
            close = difflib.get_close_matches(parts[1], phases, n=1)
            hint = f" Did you mean '{close[0]}'?" if close else ""
            err(f, f"phase folder '{parts[1]}' is not in course.yml.{hint}")
            continue
        if len(parts) == 3:
            if f.name == "README.md":
                continue
            err(f, "lessons must go inside a module folder, e.g. lessons/01-networking-fundamentals/01-tcp-ip/")
            continue

        # module folder
        modules = {m.dirname: m for m in phase.modules}
        module = modules.get(parts[2])
        if not module:
            close = difflib.get_close_matches(parts[2], modules, n=1)
            hint = f" Did you mean '{close[0]}'?" if close else ""
            err(f, f"module folder '{parts[2]}' is not in course.yml under phase {phase.dirname}.{hint}")
            continue

        # assets/ — images for this module's lessons
        if len(parts) >= 5 and parts[3] == "assets":
            if f.suffix.lower() not in IMAGE_EXT:
                err(f, f"assets/ is for images only ({', '.join(sorted(IMAGE_EXT))})")
            continue

        # code/<lesson>/ — practice code for one lesson
        if len(parts) >= 5 and parts[3] == "code":
            if len(parts) < 6:
                err(f, "code must go inside a lesson folder: code/<lesson-id>-<lesson-slug>/")
                continue
            names = {f"{l.id}-{l.slug}": l for l in module.lessons}
            if parts[4] not in names:
                close = difflib.get_close_matches(parts[4], names, n=1)
                hint = f" Did you mean '{close[0]}'?" if close else ""
                err(f, f"code folder '{parts[4]}' doesn't match any lesson in this module.{hint}")
            elif not names[parts[4]].done:
                err(f, f"code for '{parts[4]}' exists but the lesson file itself is missing")
            continue

        if len(parts) != 4:
            err(f, "unexpected folder. Inside a module only lesson .md files, assets/ and code/ are allowed")
            continue

        # lesson .md file
        if f.suffix != ".md":
            err(f, "only .md lesson files go here. Put images in assets/ and code in code/<lesson>/")
            continue
        lesson = lessons_by_path.get(r)
        if not lesson:
            by_id = {l.id: l for l in module.lessons}
            m = re.match(r"^(\d{2})-", f.name)
            if not m:
                err(f, "lesson file name must start with its two-digit id, like '01-what-is-an-ip-address.md'")
            elif m.group(1) in by_id:
                right = by_id[m.group(1)].rel_path.split("/")[-1]
                err(f, f"file name doesn't match the roadmap. Lesson {m.group(1)} must be named '{right}'")
            else:
                err(f, f"lesson {m.group(1)} is not in course.yml for module '{module.title}'. "
                       "Add it to the roadmap first, then run: python scripts/build_roadmap.py")
            continue
        check_lesson_file(lesson, f.read_text(encoding="utf-8"))


# ───────────────────────── projects ─────────────────────────

def check_projects() -> None:
    if not PROJECTS_DIR.is_dir():
        return
    root_ok = {"README.md", "PROJECT_TEMPLATE.md", ".gitkeep"}

    for f in sorted(PROJECTS_DIR.iterdir()):
        if f.is_file():
            if f.name not in root_ok:
                err(f, "don't put files directly in projects/. Make a folder: projects/<your-project-name>/")
            continue

        if not SLUG_RE.match(f.name):
            err(f, f"project folder '{f.name}' must be lowercase-words-with-dashes, e.g. 'dns-lookup-tool'")

        readme = f / "README.md"
        if not readme.is_file():
            err(f, "project needs a README.md (copy projects/PROJECT_TEMPLATE.md)")
        else:
            text = readme.read_text(encoding="utf-8")
            if not text.lstrip().startswith("# "):
                err(readme, "first line must be the project name, like '# DNS Lookup Tool'")
            if not re.search(r"\*\*Author:\*\*\s*@?\S+", text):
                err(readme, "add the author line: '**Author:** @your-github-username'")
            found = headings(text)
            for h in PROJECT_REQUIRED:
                if h not in found:
                    err(readme, f"missing required section '## {h}'")
                elif not section_body(text, h):
                    err(readme, f"section '## {h}' is empty")
            check_leftovers(readme, text)
            check_links(readme, text)

        for sub in f.rglob("*"):
            if sub.is_file():
                if sub.stat().st_size > MAX_FILE_MB * 1024 * 1024:
                    err(sub, f"file is bigger than {MAX_FILE_MB} MB")
                check_secrets(sub)


# ───────────────────────── main ─────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git base sha; skip if no course files changed")
    args = ap.parse_args()

    if args.base:
        changed = changed_files(args.base)
        relevant = [c for c in changed if c.startswith(WATCHED)]
        if not relevant:
            print("This PR doesn't touch lessons, projects or the roadmap — nothing to check. ✅")
            return 0
        print("Course files changed:\n  " + "\n  ".join(relevant))

    course = load_course()
    for e in course.errors:
        errors.append(("course.yml", e.removeprefix("course.yml: ")))

    check_lessons(course)
    check_projects()

    if build_roadmap.render() != (ROOT / "ROADMAP.md").read_text(encoding="utf-8"):
        err("ROADMAP.md", "out of date. Run: python scripts/build_roadmap.py and commit the result")

    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")

    if not errors:
        done = sum(l.done for l in course.lessons)
        msg = f"All checks passed ✅  ({done}/{len(course.lessons)} lessons published)"
        print(msg)
        if summary_path:
            Path(summary_path).write_text(f"### {msg}\n", encoding="utf-8")
        return 0

    print(f"\n❌ Found {len(errors)} problem(s):\n")
    for file, msg in errors:
        print(f"  {file}: {msg}")
        if in_ci:
            print(f"::error file={file}::{msg}")

    if summary_path:
        rows = "\n".join(f"| `{f}` | {m} |" for f, m in errors)
        Path(summary_path).write_text(
            f"### ❌ {len(errors)} problem(s) found\n\n| File | Problem |\n|---|---|\n{rows}\n",
            encoding="utf-8",
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
