# Redynox Python Internship — Toheeb Olanrewaju Olagoke

**Intern ID:** RDXINTTOHEWH86E

This repository contains all three tasks completed for the Redynox Python Developer Internship, organized in a single monorepo with a feature-branch Git workflow.

## Repository Structure
## 📦 Tasks at a Glance

| Task | Description | Folder | Tech Stack |
|------|-------------|--------|------------|
| 1 | Backend REST API with CRUD, validation, error handling, and User→Tasks relationship | `task1_backend/` | Flask, SQLite |
| 2 | File organizer with config file, scheduling, and email notifications | `task2_automation/` | Python (stdlib + `schedule`) |
| 3 | Git workflow demonstration with feature branches and pull requests | `task3_git/` | Git, GitHub |

See each task's own `README.md` for full setup instructions, features, and screenshots.

## 🌿 Branching Strategy

This project follows a **feature-branch workflow**:

| Branch | Purpose |
|--------|---------|
| `main` | Stable, reviewed code only |
| `feature/task1-backend` | Task 1 development |
| `feature/task2-automation` | Task 2 development |
| `feature/task3-git` | Task 3 documentation |

Each feature was developed on its own branch and merged into `main` via a Pull Request — never committed directly to `main`.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Olacode01/redynox-internship.git
cd redynox-internship

# Each task is self-contained — cd into the one you want
cd task1_backend
# See that task's README for setup instructions
```

## Commit Message Convention

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation update |
| `refactor:` | Code restructure without behavior change |
| `chore:` | Build, config, or tooling change |
| `test:` | Adding or updating tests |

Example: `feat: add User model with foreign key relationship to Tasks`

## Developer

**Toheeb Olanrewaju Olagoke**
Intern ID: RDXINTTOHEWH86E
