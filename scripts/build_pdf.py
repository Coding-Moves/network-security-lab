"""Build the full course as one PDF.

  python scripts/build_pdf.py                       # → dist/network-security-lab.pdf
  python scripts/build_pdf.py --edition "2026 Edition"
  python scripts/build_pdf.py --html                # also save the HTML (for debugging)

Written lessons are included in full. Missing lessons show "Coming soon".
Every lesson, code file and project links back to GitHub.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import subprocess
from collections import OrderedDict
from pathlib import Path

import markdown

from course import ROOT, github_url, load_course, load_projects, repo_slug

OUT_DIR = ROOT / "dist"
PDF_NAME = "network-security-lab.pdf"

ACADEMY_URL = "https://codingmoves.com/academy/"
LAB_URL = "https://codingmoves.com/lab/"
SITE_URL = "https://codingmoves.com/"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ───────────────────────── markdown → html ─────────────────────────

MD_EXT = ["fenced_code", "tables", "codehilite", "sane_lists", "attr_list"]
MD_CFG = {"codehilite": {"guess_lang": False, "css_class": "hl"}}


def lesson_html(lesson) -> str:
    text = lesson.path.read_text(encoding="utf-8").lstrip("﻿")
    # drop the title line and the info block — the PDF prints its own header
    text = re.sub(r"\A#\s+.*\n", "", text)
    text = re.sub(r"\A\s*(>.*\n)+", "", text)
    body = markdown.markdown(text, extensions=MD_EXT, extension_configs=MD_CFG)
    # lesson "## Section" becomes h4 under the lesson's h3
    for n in (3, 2, 1):
        body = re.sub(rf"<(/?)h{n}([ >])", rf"<\1h{n + 2}\2", body)
    return fix_links(body, lesson.path.parent)


def fix_links(body: str, base: Path) -> str:
    """Relative links → GitHub URLs. Relative images → embedded local files."""

    def href(m: re.Match) -> str:
        url = m.group(2)
        if re.match(r"^(https?:|mailto:|#)", url):
            return m.group(0)
        target = (base / url.split("#")[0]).resolve()
        try:
            rel = target.relative_to(ROOT).as_posix()
        except ValueError:
            return m.group(0)
        return f'{m.group(1)}"{github_url(rel, folder=target.is_dir())}"'

    def src(m: re.Match) -> str:
        url = m.group(2)
        if re.match(r"^(https?:|data:)", url):
            return m.group(0)
        return f'{m.group(1)}"{(base / url).resolve().as_uri()}"'

    body = re.sub(r'(href=)"([^"]+)"', href, body)
    body = re.sub(r'(src=)"([^"]+)"', src, body)
    return body


# ───────────────────────── growth history (from git) ─────────────────────────

def lesson_history(course) -> list[tuple[str, int, int]]:
    """[(month, added that month, running total)] from git history."""
    known = {l.rel_path for l in course.lessons}
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--name-only", "--format=@%cs", "--reverse", "--", "lessons/"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    first_seen: dict[str, str] = {}
    month = None
    for line in out.splitlines():
        if line.startswith("@"):
            month = line[1:8]
        elif line.strip() in known and line.strip() not in first_seen and month:
            first_seen[line.strip()] = month
    # lessons that exist but aren't committed yet (local build)
    this_month = dt.date.today().strftime("%Y-%m")
    for l in course.lessons:
        if l.done and l.rel_path not in first_seen:
            first_seen[l.rel_path] = this_month

    per_month: OrderedDict[str, int] = OrderedDict()
    for m in sorted(first_seen.values()):
        per_month[m] = per_month.get(m, 0) + 1
    rows, total = [], 0
    for m, n in per_month.items():
        total += n
        rows.append((m, n, total))
    return rows


# ───────────────────────── page sections ─────────────────────────

def bar(pct: float) -> str:
    return f'<div class="bar"><div class="fill" style="width:{pct:.1f}%"></div></div>'


def cover(course, projects, edition: str) -> str:
    total = len(course.lessons)
    done = sum(l.done for l in course.lessons)
    pct = (done / total * 100) if total else 0
    today = dt.date.today().strftime("%d %B %Y")
    return f"""
<section class="cover">
  <div class="brand">CODING MOVES · LAB · ACADEMY</div>
  <h1 class="cover-title">{esc(course.title)}</h1>
  <p class="cover-sub">{esc(course.subtitle)}</p>
  <div class="cover-stats">
    <div class="stat"><b>{done}</b><span>of {total} lessons</span></div>
    <div class="stat"><b>{pct:.0f}%</b><span>complete</span></div>
    <div class="stat"><b>{len(projects)}</b><span>community projects</span></div>
  </div>
  {bar(pct)}
  <div class="cover-meta">
    <p><b>{esc(edition)}</b> · generated {today}</p>
    <p>Source: <a href="https://github.com/{repo_slug()}">github.com/{repo_slug()}</a></p>
    <p>Course: <a href="{ACADEMY_URL}">codingmoves.com/academy</a> · Lab: <a href="{LAB_URL}">codingmoves.com/lab</a></p>
  </div>
  <p class="cover-note">This book grows with the project. Lessons not written yet are marked
  <span class="soon-tag">Coming soon</span>. Download the newest version any time from the
  <a href="https://github.com/{repo_slug()}/releases/tag/latest">latest release</a>.</p>
</section>"""


def progress_page(course, projects) -> str:
    rows = []
    for p in course.phases:
        t = len(p.lessons)
        d = sum(l.done for l in p.lessons)
        pct = (d / t * 100) if t else 0
        status = "Planned" if p.planned else f"{d} / {t}"
        rows.append(
            f"<tr><td class='num'>{p.id}</td><td>{esc(p.title)}</td>"
            f"<td class='num'>{status}</td><td class='barcell'>{bar(pct) if t else ''}</td></tr>"
        )

    hist = lesson_history(course)
    if hist:
        peak = max(n for _, n, _ in hist)
        hrows = "".join(
            f"<tr><td>{dt.datetime.strptime(m, '%Y-%m').strftime('%b %Y')}</td>"
            f"<td class='num'>+{n}</td><td class='num'>{tot}</td>"
            f"<td class='barcell'>{bar(n / peak * 100)}</td></tr>"
            for m, n, tot in hist
        )
        growth = f"""
<h2 class="plain">Growth</h2>
<p class="muted">New lessons published each month.</p>
<table class="grid"><thead><tr><th>Month</th><th>Added</th><th>Total</th><th></th></tr></thead>
<tbody>{hrows}</tbody></table>"""
    else:
        growth = ""

    return f"""
<section class="page">
<h2 class="plain" id="progress">Progress</h2>
<table class="grid"><thead><tr><th>#</th><th>Phase</th><th>Lessons</th><th></th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p class="muted">Community projects: {len(projects)}</p>
{growth}
</section>"""


def toc(course, has_projects: bool) -> str:
    items = []
    for p in course.phases:
        cls = "planned" if p.planned else ""
        items.append(f'<li class="{cls}"><a href="#phase-{p.id}">{p.id} — {esc(p.title)}</a></li>')
        for m in p.modules:
            items.append(f'<li class="mod"><a href="#mod-{p.id}-{m.id}">{esc(m.title)}</a></li>')
    items.append('<li><a href="#projects">Community Projects</a></li>')
    return f"""
<section class="page">
<h2 class="plain">Contents</h2>
<ul class="toc">
<li><a href="#progress">Progress</a></li>
<li><a href="#responsible">Responsible use</a></li>
{''.join(items)}
</ul>
</section>"""


RESPONSIBLE = """
<section class="page">
<h2 class="plain" id="responsible">Responsible use</h2>
<p>This course is for learning, defense and <b>authorized</b> testing only.</p>
<p>Do every exercise on systems you own, on intentionally vulnerable practice labs, or on systems
where you have written permission. Never scan, attack or access systems you are not allowed to.</p>
<p>Learning security also means learning responsibility.</p>
<h3 class="plain">How to read this book</h3>
<ul>
<li>Each lesson is one topic. Go in order.</li>
<li>Every lesson has a <b>View on GitHub</b> link to its source file.</li>
<li>Practice code is listed under each lesson — click a file to open it on GitHub.</li>
<li>Found a mistake? Open a "Lesson feedback" issue on GitHub.</li>
</ul>
</section>"""


def code_files(lesson) -> list[str]:
    d = ROOT / lesson.code_rel_dir
    if not d.is_dir():
        return []
    return sorted(p.relative_to(ROOT).as_posix() for p in d.rglob("*") if p.is_file() and p.name != ".gitkeep")


def lesson_block(lesson) -> str:
    head = (
        f'<div class="lesson-kicker">Lesson {lesson.phase.id}.{lesson.module.id}.{lesson.id}'
        f" · {esc(lesson.module.title)}</div>"
        f'<h3 id="l-{lesson.phase.id}-{lesson.module.id}-{lesson.id}">{esc(lesson.title)}</h3>'
    )
    if not lesson.done:
        return f"""
<article class="lesson soon">{head}
<div class="soon-box"><span class="soon-tag">Coming soon</span>
This lesson isn't written yet. Follow progress on
<a href="https://github.com/{repo_slug()}">GitHub</a>.</div>
</article>"""

    links = [f'<a class="btn" href="{github_url(lesson.rel_path)}">View on GitHub</a>']
    files = code_files(lesson)
    code_list = ""
    if files:
        lis = "".join(
            f'<li><a href="{github_url(f)}">{esc(f.split("/code/", 1)[1].split("/", 1)[1])}</a></li>' for f in files
        )
        code_list = f'<div class="code-box"><b>Practice code</b> — click to open on GitHub<ul>{lis}</ul></div>'
    return f"""
<article class="lesson">{head}
<div class="links">{''.join(links)}</div>
{lesson_html(lesson)}
{code_list}
</article>"""


def phase_block(p) -> str:
    out = [f'<section class="phase"><div class="phase-num">Phase {p.id}</div>'
           f'<h1 id="phase-{p.id}">{esc(p.title)}</h1>']
    if p.planned:
        out.append('<div class="soon-box big"><span class="soon-tag">Coming soon</span> This phase is planned.</div>')
        if p.summary:
            out.append(f'<p class="summary"><b>What it will cover:</b> {esc(p.summary)}</p>')
        if p.note:
            out.append(f'<p class="note">{esc(p.note)}</p>')
        out.append("</section>")
        return "".join(out)

    d, t = sum(l.done for l in p.lessons), len(p.lessons)
    out.append(f'<p class="muted">{d} of {t} lessons published</p>')
    for m in p.modules:
        out.append(f'<h2 id="mod-{p.id}-{m.id}">{esc(m.title)}</h2>')
        out.append('<ol class="mod-list">' + "".join(
            f'<li class="{"done" if l.done else "todo"}">{esc(l.title)}'
            f'{"" if l.done else " <span class=soon-tag>soon</span>"}</li>'
            for l in m.lessons) + "</ol>")
        for l in m.lessons:
            out.append(lesson_block(l))
    out.append("</section>")
    return "".join(out)


def projects_block(course, projects) -> str:
    out = ['<section class="phase"><div class="phase-num">Community</div>'
           '<h1 id="projects">Community Projects</h1>']
    if projects:
        for pr in projects:
            author = f' · by {esc(pr.author)}' if pr.author else ""
            out.append(
                f'<div class="project"><h3>{esc(pr.title)}</h3>'
                f'<p class="muted">projects/{esc(pr.slug)}{author}</p>'
                f'<p>{esc(pr.summary)}</p>'
                f'<a class="btn" href="{github_url(pr.rel_dir, folder=True)}">Open project on GitHub</a></div>'
            )
    else:
        out.append('<div class="soon-box big"><span class="soon-tag">Coming soon</span> '
                   'No community projects yet — be the first!</div>')
    if course.project_ideas:
        out.append("<h2>Project ideas</h2><ol>" + "".join(f"<li>{esc(i)}</li>" for i in course.project_ideas) + "</ol>")
    out.append(f'<p>Want to add a project? Read '
               f'<a href="{github_url("CONTRIBUTING.md")}">CONTRIBUTING.md</a>.</p></section>')
    return "".join(out)


# ───────────────────────── css ─────────────────────────

def css() -> str:
    from pygments.formatters import HtmlFormatter
    pyg = HtmlFormatter(style="friendly").get_style_defs(".hl")
    return """
@page { size: A4; margin: 22mm 18mm 20mm 18mm;
  @bottom-left { content: "Network Security Lab · Coding Moves"; font-size: 8pt; color: #8a94a6; }
  @bottom-right { content: counter(page); font-size: 8pt; color: #8a94a6; } }
@page :first { margin: 0; @bottom-left { content: none } @bottom-right { content: none } }
:root { --ink:#0f172a; --muted:#64748b; --line:#e2e8f0; --accent:#0e7490; --accent-soft:#ecfeff; --soon:#b45309; --soon-soft:#fffbeb; }
body { margin: 0; }
html { font-family: "Noto Sans", "DejaVu Sans", sans-serif; font-size: 10pt; color: var(--ink); line-height: 1.55; }
a { color: var(--accent); text-decoration: none; }
h1,h2,h3,h4 { line-height: 1.25; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.6pt; }
p code, li code { background:#f1f5f9; padding: 0 3px; border-radius: 3px; }
pre { background:#f8fafc; border:1px solid var(--line); border-radius:6px; padding:8px 10px; white-space: pre-wrap; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th, td { border-bottom: 1px solid var(--line); padding: 4px 6px; text-align: left; vertical-align: middle; }
th { font-size: 8.5pt; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.num { white-space: nowrap; width: 1%; }
.barcell { width: 35%; }
.muted { color: var(--muted); }

/* cover */
.cover { page: first; height: 297mm; padding: 38mm 22mm 0; box-sizing: border-box;
  background: #0f172a; color: #e2e8f0; page-break-after: always; }
.cover a { color: #67e8f9; }
.brand { letter-spacing: .25em; font-size: 9pt; color: #67e8f9; font-weight: bold; }
.cover-title { font-size: 34pt; margin: 14mm 0 4mm; color: #fff; bookmark-level: none; }
.cover-sub { font-size: 13pt; color: #cbd5e1; margin: 0 0 16mm; }
.cover-stats { display: flex; gap: 10mm; margin-bottom: 5mm; }
.stat b { display:block; font-size: 22pt; color:#fff; }
.stat span { font-size: 9pt; color:#94a3b8; }
.cover .bar { background:#1e293b; }
.cover-meta { margin-top: 14mm; font-size: 9.5pt; color:#cbd5e1; }
.cover-meta p { margin: 2px 0; }
.cover-note { margin-top: 18mm; font-size: 9pt; color:#94a3b8; max-width: 140mm; }

.bar { height: 6px; background: var(--line); border-radius: 3px; overflow: hidden; }
.fill { height: 100%; background: var(--accent); }

.page { page-break-after: always; }
h2.plain, h3.plain { bookmark-level: none; }
.page h2.plain { font-size: 18pt; margin-top: 0; }
#progress, #responsible { bookmark-level: 1; }

/* toc */
.toc { list-style: none; padding: 0; }
.toc li { margin: 2px 0; }
.toc li a::after { content: leader('.') target-counter(attr(href), page); color: var(--muted); }
.toc li a { color: var(--ink); display: block; }
.toc li.mod { padding-left: 8mm; font-size: 9pt; }
.toc li.mod a { color: var(--muted); }
.toc li.planned a { color: var(--muted); }

/* phases */
.phase { page-break-before: always; }
.phase-num { color: var(--accent); font-weight: bold; letter-spacing: .15em; text-transform: uppercase; font-size: 9pt; }
.phase h1 { font-size: 24pt; margin: 2px 0 4px; bookmark-level: 1; }
.phase > h2 { font-size: 15pt; border-bottom: 2px solid var(--accent); padding-bottom: 3px; margin-top: 10mm; bookmark-level: 2; }
.mod-list li.todo { color: var(--muted); }
.summary { margin-top: 6mm; }
.note { border-left: 3px solid var(--soon); padding-left: 8px; color: var(--soon); }

/* lessons */
.lesson { margin-top: 8mm; padding-top: 4mm; border-top: 1px solid var(--line); }
.lesson:not(.soon) { page-break-before: always; border-top: none; }
.lesson-kicker { color: var(--muted); font-size: 8.5pt; text-transform: uppercase; letter-spacing: .06em; }
.lesson h3 { font-size: 15pt; margin: 2px 0 6px; bookmark-level: 3; }
.lesson.soon h3 { font-size: 11.5pt; color: var(--muted); }
.lesson h4 { font-size: 11.5pt; color: var(--accent); margin: 6mm 0 2mm; bookmark-level: none; }
.lesson h5, .lesson h6 { bookmark-level: none; }
.links { margin-bottom: 4mm; }
.btn { display: inline-block; border: 1px solid var(--accent); border-radius: 4px; padding: 2px 8px; font-size: 8.5pt; margin-right: 4px; }
.soon-tag { display: inline-block; background: var(--soon-soft); color: var(--soon); border: 1px solid #fcd34d;
  border-radius: 3px; font-size: 7.5pt; padding: 0 5px; font-weight: bold; text-transform: uppercase; letter-spacing: .04em; }
.soon-box { background: var(--soon-soft); border: 1px dashed #fcd34d; border-radius: 6px; padding: 6px 10px; font-size: 9pt; }
.soon-box.big { padding: 12px 14px; font-size: 10pt; margin-top: 6mm; }
.code-box { background: var(--accent-soft); border: 1px solid #a5f3fc; border-radius: 6px; padding: 6px 10px; margin-top: 6mm; font-size: 9pt; }
.code-box ul { margin: 4px 0 0; }
img { max-width: 100%; }

/* projects */
.project { border: 1px solid var(--line); border-radius: 6px; padding: 8px 12px; margin: 5mm 0; }
.project h3 { margin: 0; bookmark-level: 2; }
""" + pyg


# ───────────────────────── main ─────────────────────────

def build(edition: str, save_html: bool) -> Path:
    course = load_course()
    if course.errors:
        raise SystemExit("course.yml has errors — run python scripts/validate.py")
    projects = load_projects()

    body = (
        cover(course, projects, edition)
        + toc(course, bool(projects))
        + progress_page(course, projects)
        + RESPONSIBLE
        + "".join(phase_block(p) for p in course.phases)
        + projects_block(course, projects)
    )
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(course.title)}</title><meta name="author" content="Coding Moves">
<style>{css()}</style></head><body>{body}</body></html>"""

    OUT_DIR.mkdir(exist_ok=True)
    if save_html:
        (OUT_DIR / "course.html").write_text(doc, encoding="utf-8")

    from weasyprint import HTML
    out = OUT_DIR / PDF_NAME
    HTML(string=doc, base_url=str(ROOT)).write_pdf(out)
    done = sum(l.done for l in course.lessons)
    print(f"Wrote {out.relative_to(ROOT)} — {done}/{len(course.lessons)} lessons, {len(projects)} projects")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", default="Latest edition")
    ap.add_argument("--html", action="store_true")
    a = ap.parse_args()
    build(a.edition, a.html)
