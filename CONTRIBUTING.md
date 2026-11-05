# Contributing

Thanks for helping! Please read this before opening a pull request.

## Who does what

| Who          | Can do                                                        |
| ------------ | ------------------------------------------------------------- |
| Maintainer   | Writes and edits lessons, roadmap and all repo files          |
| Contributors | Add projects in `projects/` · review lessons and give feedback |

**Contributors cannot change lesson files** (or anything outside `projects/`).
A check runs on every pull request. If your PR changes files outside `projects/`, it will fail and can't be merged.

---

## 1. Adding a project

1. Fork the repo.
2. Create a new folder: `projects/your-project-name/` (lowercase, use `-` between words).
3. Add a `README.md` inside it using the [project template](projects/PROJECT_TEMPLATE.md).
4. Add your code in the same folder.
5. Open a pull request.

**Project rules**

- One project per pull request.
- Only change files inside **your own** project folder.
- The project must be legal and safe — no malware, no tools built to attack systems you don't own.
- Anything that scans or tests must clearly say it is for **authorized targets only**.
- Never include passwords, API keys, personal data or real target addresses.
- Explain how to run it and how you tested it.
- Code is shared under the [MIT License](LICENSE).

## 2. Reviewing lessons

Found a mistake, an old command, or something unclear? Great — tell us.

- **On an open lesson PR:** leave a review comment on the line.
- **On a published lesson:** open a [Lesson feedback](../../issues/new?template=lesson-feedback.yml) issue.

Please include:

- Which lesson (file name or link)
- What is wrong or unclear
- Your suggested fix, and a source if you have one

The maintainer will check it and update the lesson.

---

## Pull request checklist

- [ ] My changes are only inside `projects/<my-project>/`
- [ ] I added a README using the template
- [ ] No secrets, personal data or real targets
- [ ] I tested it and explained how

## Be respectful

Be kind, give useful feedback, and help beginners. Security knowledge is for protecting people.
