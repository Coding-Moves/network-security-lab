"""Shared helpers: load course.yml and work out lesson / project paths."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
PROJECTS_DIR = ROOT / "projects"
COURSE_FILE = ROOT / "course.yml"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RE = re.compile(r"^\d{2}$")

# Sections a lesson MUST have (as "## Heading").
LESSON_REQUIRED = [
    "Objective",
    "Explanation",
    "Check your understanding",
    "References",
]
# All sections a lesson MAY have, in this order.
LESSON_ALLOWED = [
    "Objective",
    "Explanation",
    "How it works",
    "Examples",
    "Commands",
    "Practical work",
    "Common mistakes",
    "Why it matters for security",
    "Check your understanding",
    "References",
]

# Sections a project README MUST have.
PROJECT_REQUIRED = [
    "What it does",
    "How to run",
    "How I tested it",
    "Safety note",
]


def repo_slug() -> str:
    return os.environ.get("GITHUB_REPOSITORY", "Coding-Moves/network-security-lab")


def branch() -> str:
    return os.environ.get("COURSE_BRANCH", "main")


def github_url(rel_path: str, folder: bool = False) -> str:
    kind = "tree" if folder else "blob"
    return f"https://github.com/{repo_slug()}/{kind}/{branch()}/{rel_path}"


@dataclass
class Lesson:
    id: str
    slug: str
    title: str
    phase: "Phase"
    module: "Module"

    @property
    def rel_path(self) -> str:
        return f"lessons/{self.phase.dirname}/{self.module.dirname}/{self.id}-{self.slug}.md"

    @property
    def path(self) -> Path:
        return ROOT / self.rel_path

    @property
    def code_rel_dir(self) -> str:
        """Practice code for a lesson lives next to it: <module>/code/<lesson-id>-<slug>/"""
        return f"lessons/{self.phase.dirname}/{self.module.dirname}/code/{self.id}-{self.slug}"

    @property
    def done(self) -> bool:
        return self.path.is_file()


@dataclass
class Module:
    id: str
    slug: str
    title: str
    phase: "Phase"
    lessons: list[Lesson] = field(default_factory=list)

    @property
    def dirname(self) -> str:
        return f"{self.id}-{self.slug}"


@dataclass
class Phase:
    id: str
    slug: str
    title: str
    summary: str = ""
    note: str = ""
    modules: list[Module] = field(default_factory=list)

    @property
    def dirname(self) -> str:
        return f"{self.id}-{self.slug}"

    @property
    def planned(self) -> bool:
        return not any(m.lessons for m in self.modules)

    @property
    def lessons(self) -> list[Lesson]:
        return [l for m in self.modules for l in m.lessons]


@dataclass
class Course:
    title: str
    subtitle: str
    phases: list[Phase]
    project_ideas: list[str]
    errors: list[str]

    @property
    def lessons(self) -> list[Lesson]:
        return [l for p in self.phases for l in p.lessons]


def _check_item(kind: str, item: dict, where: str, errors: list[str]) -> bool:
    ok = True
    for key in ("id", "slug", "title"):
        if not item.get(key):
            errors.append(f"course.yml: {kind} at {where} is missing '{key}'")
            ok = False
    if not ok:
        return False
    if not ID_RE.match(str(item["id"])):
        errors.append(f"course.yml: {kind} '{item['title']}' id must be two digits like \"01\" (got {item['id']!r}). Put it in quotes.")
        ok = False
    if not SLUG_RE.match(str(item["slug"])):
        errors.append(f"course.yml: {kind} '{item['title']}' slug '{item['slug']}' must be lowercase-words-with-dashes")
        ok = False
    return ok


def load_course() -> Course:
    data = yaml.safe_load(COURSE_FILE.read_text(encoding="utf-8")) or {}
    errors: list[str] = []
    phases: list[Phase] = []

    seen_phase_ids: set[str] = set()
    for p in data.get("phases") or []:
        if not _check_item("phase", p, "top level", errors):
            continue
        pid = str(p["id"])
        if pid in seen_phase_ids:
            errors.append(f"course.yml: phase id {pid} is used twice")
        seen_phase_ids.add(pid)
        phase = Phase(pid, p["slug"], p["title"], p.get("summary", ""), p.get("note", ""))

        seen_mod: set[str] = set()
        for m in p.get("modules") or []:
            if not _check_item("module", m, f"phase {pid}", errors):
                continue
            mid = str(m["id"])
            if mid in seen_mod:
                errors.append(f"course.yml: module id {mid} is used twice in phase {pid}")
            seen_mod.add(mid)
            module = Module(mid, m["slug"], m["title"], phase)

            seen_les: set[str] = set()
            seen_slug: set[str] = set()
            for l in m.get("lessons") or []:
                if not _check_item("lesson", l, f"phase {pid} / module {mid}", errors):
                    continue
                lid = str(l["id"])
                if lid in seen_les:
                    errors.append(f"course.yml: lesson id {lid} is used twice in {phase.dirname}/{module.dirname}")
                if l["slug"] in seen_slug:
                    errors.append(f"course.yml: lesson slug '{l['slug']}' is used twice in {phase.dirname}/{module.dirname}")
                seen_les.add(lid)
                seen_slug.add(l["slug"])
                module.lessons.append(Lesson(lid, l["slug"], l["title"], phase, module))
            phase.modules.append(module)
        phases.append(phase)

    return Course(
        title=data.get("title", "Course"),
        subtitle=data.get("subtitle", ""),
        phases=phases,
        project_ideas=data.get("project_ideas") or [],
        errors=errors,
    )


@dataclass
class Project:
    slug: str
    title: str
    author: str
    summary: str

    @property
    def rel_dir(self) -> str:
        return f"projects/{self.slug}"


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def load_projects() -> list[Project]:
    projects = []
    if not PROJECTS_DIR.is_dir():
        return projects
    for d in sorted(PROJECTS_DIR.iterdir()):
        readme = d / "README.md"
        if not d.is_dir() or not readme.is_file():
            continue
        text = readme.read_text(encoding="utf-8")
        title_m = re.search(r"^#\s+(.+)$", text, re.M)
        author_m = re.search(r"\*\*Author:\*\*\s*(.+)", text)
        summary = _section(text, "What it does").split("\n\n")[0].strip()
        projects.append(
            Project(
                slug=d.name,
                title=title_m.group(1).strip() if title_m else d.name,
                author=author_m.group(1).strip() if author_m else "",
                summary=summary,
            )
        )
    return projects


def headings(text: str) -> list[str]:
    """All level-2 headings, outside code blocks."""
    out, in_code = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            m = re.match(r"^##\s+(.+?)\s*#*\s*$", line)
            if m:
                out.append(m.group(1).strip())
    return out
