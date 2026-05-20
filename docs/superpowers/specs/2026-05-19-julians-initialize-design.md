# `julians-initialize` — Tarra onboarding branch design

**Date:** 2026-05-19
**Author:** Julian (with Claude)
**Audience:** Julian (for review); the implementing Claude session next; Ilai indirectly (through what this produces)

## Goal

Hand Ilai a Tarra branch that, when he opens it in Claude Code for the first time, walks him through a guided onboarding. The onboarding captures what Tarra is, how the code is structured, what features are in flight, and what's shaky — populating a real documentation skeleton along the way. When onboarding finishes, the scaffolding deletes itself, a real `CLAUDE.md` replaces the starter, and the branch is ready to merge into `main`.

Two side goals:
1. **De-Replit Tarra.** Ilai started the project on Replit and is migrating to Claude Code. The branch removes Replit-specific files and restructures the code into a conventional Python `src/` layout so it runs locally without Replit's scaffolding.
2. **Teach by doing.** Concepts like TDD and using agents in parallel are introduced briefly during onboarding, never as lectures. After onboarding completes, those concepts are gone from the repo — Ilai develops his own working style with Claude from there.

## Non-goals

- Not a comprehensive tutorial on Claude Code, Python, Flask, or software engineering practice. The onboarding is a one-shot bootstrap, not a course.
- Not refactoring Ilai's application logic. Code changes are mechanical only: import paths, template paths, file locations.
- Not setting up CI/CD, deployment, testing frameworks beyond what already exists, or any production tooling. School project scope.

## Design overview

The branch goes through two phases.

### Phase 1 — Julian sets up the branch (one-shot, before handoff)

Performed by Julian in this session, on the `julians-initialize` branch.

**De-Replit:**
- Delete `.replit`.
- In `pyproject.toml`, rename `name = "python-template"` → `name = "tarra"`.
- Keep `gunicorn` in dependencies (legitimate production server, not Replit-specific); make `flask --app src.app run` the documented dev command.

**Refactor (mechanical only):**
- `main.py` → `src/app.py`
- `templates/index.html` → `src/templates/index.html`
- `test_basic_pitch.py` → `tests/test_basic_pitch.py`
- Fix the import in the test file (it currently imports `main`; update to import from the new module path).
- Update `.gitignore` to ensure `uploads/` is ignored.
- No logic changes to `app.py`. Template path resolution relies on Flask's default behavior (looks for `templates/` next to the app module), which works without code changes after the move.

**Verify:**
- Fresh install: `poetry install` (or pip equivalent).
- Run the app: `flask --app src.app run`. Hit the upload flow with a sample audio file. Confirm 200 response and Basic Pitch fallback behavior matches the original.
- Run the test script: `python tests/test_basic_pitch.py`. Confirm it produces the same output as before.
- If any of this fails, fix before committing. The branch is not shippable until it runs.

**Add documentation scaffolding:**

```
README.md                 (placeholder; intake fills it during Phase 2)
CLAUDE.md                 (STARTER, self-replacing — see below)
ROADMAP.md                (skeleton with Now / Next / Later headings)
docs/
├── architecture.md       (empty — intake fills)
├── ideas/
│   └── README.md         (explains the folder)
├── specs.md              (append-only running list of specs)
└── tech-debt.md          (one seed entry about basic-pitch dependency)
```

**Add `JULIANS-HELP/`:**

```
JULIANS-HELP/
├── 00-START-HERE.md
├── 01-intake.md
├── 02-setup.md
├── 03-finalize.md
└── SCHOOL-SUBMISSION-NOTE.md
```

(File-by-file content described below.)

**Commit and push.**

### Phase 2 — Ilai onboards on the branch (driven by Claude Code)

When Ilai checks out the branch and opens Claude Code:

1. Starter `CLAUDE.md` auto-loads. It contains a short instruction: *"If `JULIANS-HELP/` exists in this repo, you are in onboarding mode. Read `JULIANS-HELP/00-START-HERE.md` and follow it. Do not begin coding work until onboarding is complete."*
2. Claude reads `00-START-HERE.md`, which lays out the four steps: intake → setup → finalize, and the school-submission note for reference.
3. **Intake (`01-intake.md`).** Claude conducts the conversation with Ilai. Questions and the docs they populate:
   - *"What does Tarra do? Explain it like you'd tell a friend."* → `README.md` (draft section).
   - *"Walk me through how the pieces fit together — front-end, Flask, Basic Pitch, what happens when you upload a file."* → `docs/architecture.md`.
   - *"What features exist right now that you're happy with?"* → `ROADMAP.md` (Now column).
   - *"What features are you working on or want to add?"* → `ROADMAP.md` (Next column) and `docs/ideas/`.
   - *"What feels shaky or hacky right now?"* → `docs/tech-debt.md`.
   - Claude writes drafts as Ilai talks; Ilai confirms before moving on.
4. **Setup (`02-setup.md`).** Claude:
   - First shows the file-relocation map (where his code went after the refactor).
   - Walks Ilai through installing Claude Code (if not already), then installing the `obra/superpowers` plugin.
   - Verifies superpowers loaded.
   - Surfaces one short paragraph each on TDD and on parallel-vs-sequential agents — once, in passing, not as a lesson.
5. **Finalize (`03-finalize.md`).** Claude:
   - Asks Ilai if he's ready to graduate. Explains plainly what will happen: starter CLAUDE.md replaced with a real one based on his intake answers, `JULIANS-HELP/` deleted, all committed.
   - On confirmation: writes a fresh `CLAUDE.md` (project description, how to run, conventions, where docs live, links to architecture and roadmap). Deletes `JULIANS-HELP/`. Commits with message `Onboarding complete — graduate to real CLAUDE.md`.
6. Ilai (or Julian) merges `julians-initialize` → `main`.

## Detailed file contents

### Starter `CLAUDE.md` (Phase 1)

Short. Roughly:

> This is the Tarra repo. Ilai is the developer; he's a high school student migrating from Replit to Claude Code.
>
> If `JULIANS-HELP/` exists in this repo, you are in **onboarding mode**. Do not start coding work. Instead:
> 1. Read `JULIANS-HELP/00-START-HERE.md`
> 2. Follow the steps it lays out, in order
> 3. The final step (`03-finalize.md`) will replace this file with a real CLAUDE.md
>
> Tone for the onboarding conversation: calm, brief, dry. Ilai is a smart kid; explain things in one or two sentences, not paragraphs. No cheerleading.

### `JULIANS-HELP/00-START-HERE.md`

Greets Claude (not Ilai). Says: here are the four files, read them in order, here's the high-level flow. Reminds about tone. Specifies that intake answers should be written to specific doc files as Claude goes (not held until the end).

### `JULIANS-HELP/01-intake.md`

Question script with `→ writes to:` annotations next to each question. Includes a directive to confirm with Ilai before writing each section, and to keep drafts brief — README is a paragraph or two, architecture is one page, not a thesis.

### `JULIANS-HELP/02-setup.md`

Opens with the file-relocation map (table of where his Replit-era files went). Then:
- Install Claude Code (link).
- Install `obra/superpowers` plugin from GitHub.
- Verify with a quick check.
- One short paragraph on TDD: *"When you want to add a function, you can write a test that fails first, then make it pass. Tells you immediately if your code does what you said it would. I'll usually offer it; you can say yes or no."*
- One short paragraph on agents: *"Sometimes a task has steps that depend on each other (do A, then B with A's result). Sometimes the steps are independent. When they're independent, I can dispatch them in parallel — faster. I'll just do it when it makes sense."*

### `JULIANS-HELP/03-finalize.md`

Confirmation prompt for Ilai. Plain language about what's about to happen. Then the rewrite-and-delete instructions for Claude, with a template for the new CLAUDE.md (project summary, run command, where docs live, conventions Ilai confirmed during intake).

### `JULIANS-HELP/SCHOOL-SUBMISSION-NOTE.md`

Short note: this branch added some scaffolding for your migration. If your teacher would find the onboarding scaffolding weird in your submission, the relevant commits are listed here — you can squash or revert. The final state on `main` after onboarding completes is clean; this note is only relevant if a teacher reviews the branch history.

### `docs/tech-debt.md` seed entry

One bullet, in plain language Ilai will understand:

> - `basic-pitch` is imported in `src/app.py` but isn't listed in `pyproject.toml` as a dependency. If someone clones the repo and installs deps, the import will silently fail and the app will run in fallback mode (no actual note detection). Fix: add `basic-pitch = "^X.Y"` to `pyproject.toml`.

### `docs/specs.md` skeleton

A one-paragraph header explaining what a spec is and when to write one (*"before building a feature, jot down: what are you making, why, and what does done look like. One section per feature, append-only."*), followed by an example section so the format is clear.

### `docs/ideas/README.md`

Two sentences: *"Drop one file in here per raw idea — 'what if Tarra could detect tuning automatically' kind of thing. Low ceremony. If an idea gets serious, it graduates to a section in `specs.md`."*

## Risks and mitigations

- **Flask template path:** Moving `templates/` into `src/` works because Flask's `Flask(__name__)` resolves template paths relative to the module's location. Verified at the documentation level; will verify at runtime in Phase 1.
- **`basic-pitch` undeclared:** Not a blocker for Phase 1 — the existing code uses try/except around the import and runs without it. Flagged as the tech-debt seed entry so Ilai sees it during onboarding.
- **Claude re-firing onboarding:** Once `JULIANS-HELP/` is deleted in Phase 2 step 5, the starter CLAUDE.md is also replaced. So the trigger condition (folder exists) can't fire again.
- **Tone drift:** The starter CLAUDE.md, `00-START-HERE.md`, and each numbered file all repeat the tone directive. Redundant but cheap.
- **Branch hygiene for school submission:** Addressed by `SCHOOL-SUBMISSION-NOTE.md` and by the fact that the final post-onboarding commit produces a clean state.

## Implementation order (for the next session)

1. Confirm on `julians-initialize` branch.
2. Phase 1 refactor: delete `.replit`, rename pyproject, move files, fix imports.
3. Verify the app runs and the test passes.
4. Write the scaffolding files (docs/ skeleton, JULIANS-HELP/, starter CLAUDE.md, README, ROADMAP).
5. Commit, push, hand off to Ilai.
