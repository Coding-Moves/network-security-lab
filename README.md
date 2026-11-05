# Network Security Lab

**Learn networking. Understand security. Think like a security engineer.**

[Coding Moves](https://codingmoves.com/) · [Lab](https://codingmoves.com/lab/) · [Academy](https://codingmoves.com/academy/) · Open Source

---

## What is this?

A free, step-by-step learning path for networking and ethical security.

We start with the basics — how computers talk, how the internet works, DNS, HTTPS, firewalls, Linux — and slowly move to network investigation, web security, vulnerability assessment and authorized security testing.

Every lesson is small, focused on one topic, and has a practical exercise.

## How it is organized

| Level  | Example                  |
| ------ | ------------------------ |
| Phase  | 01 — Networking          |
| Module | TCP/IP                   |
| Lesson | What is an IP address?   |

One lesson = one topic. A new lesson is added about once a day.

```
course.yml                   → the course plan (source of the roadmap)
ROADMAP.md                   → generated from course.yml
lessons/                     → the course (written by the maintainer)
  01-networking-fundamentals/
    01-tcp-ip/
      01-what-is-an-ip-address.md
      code/01-what-is-an-ip-address/   → practice code for that lesson
      assets/                          → images
projects/                    → projects built by the community
scripts/                     → checks, roadmap and PDF builders
```

## Download the course as a PDF

📘 **[Download the latest PDF](../../releases/download/latest/network-security-lab.pdf)**

The PDF is rebuilt automatically every time something is merged. It has every published lesson, "Coming soon" for the rest, clickable links to each lesson, its practice code and the community projects on GitHub, and a progress page showing how the course grows. A yearly edition is saved every 1 January in [Releases](../../releases).

## Where to start

1. Read the [Roadmap](ROADMAP.md) to see what's coming.
2. Open `lessons/` and start from `00-getting-started`.
3. Do the practical work at the end of each lesson.

## Want to contribute?

The lessons are written and maintained by Coding Moves.
As a contributor you can:

- **Add a project** to `projects/` through a pull request.
- **Review lessons** — suggest fixes, point out mistakes, or ask questions by opening a [Lesson feedback](../../issues/new?template=lesson-feedback.yml) issue or commenting on a lesson pull request.

Contributors cannot edit lesson files directly. Read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Responsible use

This project is for learning, defense and **authorized** testing only.

Do every exercise on systems you own, on intentionally vulnerable practice labs, or on systems where you have written permission.

Never scan, attack or access systems you are not allowed to. Learning security also means learning responsibility.

## Part of Coding Moves

- **[Coding Moves Lab](https://codingmoves.com/lab/)** — where this project is built and tested in the open.
- **[Coding Moves Academy](https://codingmoves.com/academy/)** — where the lessons are published as a course.

## License

- Lessons and written content: [CC BY 4.0](LICENSE-CONTENT.md)
- Code and scripts: [MIT](LICENSE)

---

**Learn one concept. Test it. Document it. Move forward.**
