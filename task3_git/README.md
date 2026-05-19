# Task 3 — Git & Collaboration Workflow

This task demonstrates real-world Git collaboration practices: feature branching, conventional commits, pull requests, and structured documentation.

##  Objective

Demonstrate the ability to work in a real development environment by using Git properly — not just as a backup tool, but as a collaboration platform.

##  What This Task Demonstrates

-  **Repository creation** on GitHub with a clean monorepo structure
-  **Feature-branch workflow** — every change happens on its own branch
-  **Conventional commit messages** with clear, descriptive prefixes
-  **Pull Request workflow** — code review before merging to `main`
-  **Structured documentation** — README at the root and per-task
- **`.gitignore` hygiene** — auto-generated files, virtualenvs, and OS junk excluded

##  Strategy

Each task lives on its own feature branch. The `main` branch holds reviewed, stable code only.
### Creating a feature branch

```bash
git checkout main
git pull origin main
git checkout -b feature/task1-backend
# ... make changes ...
git add .
git commit -m "feat: add Flask REST API with CRUD endpoints"
git push -u origin feature/task1-backend
```

### Opening a Pull Request

After pushing a branch, open a PR on GitHub:
1. Visit the repo on GitHub
2. Click **Compare & pull request**
3. Write a clear title and description
4. Request review (or self-review for solo projects)
5. Merge once approved

## 📝 Commit Convention

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `feat:` | A new feature | `feat: add user authentication endpoint` |
| `fix:` | A bug fix | `fix: handle missing JSON body in POST /tasks` |
| `docs:` | Documentation only | `docs: add API endpoint table to README` |
| `refactor:` | Code change that doesn't add features or fix bugs | `refactor: extract validation into helper function` |
| `chore:` | Tooling / config changes | `chore: add .gitignore for venv and logs` |
| `test:` | Adding or modifying tests | `test: add integration test for user creation` |

### Why conventional commits matter

- **Readable history** — `git log --oneline` becomes a story of the project
- **Easier reviews** — reviewers know the intent of each change
- **Automatable** — tools can generate changelogs from commit history

##  .gitignore Hygiene

The root `.gitignore` excludes:

- **macOS junk** (`.DS_Store`)
- **Python caches** (`__pycache__/`, `*.pyc`)
- **Virtual environments** (`venv/`, `.venv/`)
- **IDE configs** (`.vscode/`, `.idea/`)
- **Task 1 runtime files** (`tasks.db`)
- **Task 2 runtime files** (`logs/`, `test_files/`, `junk_folder/`)

Keeping these out of git means:
- Smaller, faster clones
- No leaking of personal paths or local state
- Clean diffs that show only meaningful changes

##  Workflow Used for This Project

1. **Initialize** the repository locally with `main` as the default branch
2. **Add the root scaffolding** (README, .gitignore, INSTRUCTIONS) — committed to `main`
3. **For each task:**
   - Create a feature branch from `main`
   - Add the task's code in its subfolder
   - Commit with a conventional message
   - Push the branch to GitHub
   - Open a Pull Request
   - Merge into `main`
4. **Final state** — `main` has the full project; each feature branch's history is preserved on GitHub for reference

## Useful Commands

```bash
# See all branches (local + remote)
git branch -a

# See commit history in graph form
git log --oneline --graph --all

# Check which branch you're on
git status

# Switch branches
git checkout feature/task1-backend

# Update local main from GitHub
git checkout main && git pull origin main

# Delete a merged branch locally
git branch -d feature/task1-backend
```

## Developer

**Toheeb Olanrewaju Olagoke**
Intern ID: RDXINTTOHEWH86E
