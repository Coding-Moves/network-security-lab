# Lessons

The course, one topic per file. Start from `00-getting-started` and go in order.

## Structure

```
lessons/
  <phase-id>-<phase-slug>/
    <module-id>-<module-slug>/
      <lesson-id>-<lesson-slug>.md       ← the lesson
      code/<lesson-id>-<lesson-slug>/    ← practice code (optional)
      assets/                            ← images (optional)
```

Example:

```
lessons/01-networking-fundamentals/01-tcp-ip/01-what-is-an-ip-address.md
lessons/01-networking-fundamentals/01-tcp-ip/code/01-what-is-an-ip-address/show_ip.py
```

All ids, slugs and titles come from [`course.yml`](../course.yml). The file name must match exactly — the PR check will tell you the right name if it's wrong.

## Adding a lesson (maintainer)

1. Find the lesson in `course.yml`. If it's new, add a line there first.
2. Copy [`LESSON_TEMPLATE.md`](../LESSON_TEMPLATE.md) to the right path.
3. Write it. Required sections: Objective, Explanation, Check your understanding, References.
4. Run:
   ```bash
   pip install -r scripts/requirements.txt
   python scripts/build_roadmap.py   # updates ROADMAP.md
   python scripts/validate.py        # same check as the PR
   python scripts/build_pdf.py       # optional: preview the PDF in dist/
   ```
5. Commit everything (lesson + ROADMAP.md) and open a PR.

> Lessons are written by the maintainer. Found a problem? Open a "Lesson feedback" issue.
