# `julians-initialize` Branch Setup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up the `julians-initialize` branch with a de-Replit'd, `src/`-layout Tarra plus self-deleting onboarding scaffolding (`JULIANS-HELP/`) and docs skeleton.

**Architecture:** Two phases — Phase 1 (this plan) is mechanical refactor + scaffolding written into the branch by Julian's session. Phase 2 (driven by Ilai's future session on the branch) is executed by Claude reading `JULIANS-HELP/`; this plan does not implement Phase 2.

**Tech Stack:** Python 3.11, Flask, Poetry, Markdown.

**Spec:** [docs/superpowers/specs/2026-05-19-julians-initialize-design.md](../specs/2026-05-19-julians-initialize-design.md)

---

## Pre-flight

This plan must be executed from the `julians-initialize` branch in the Tarra repo. The branch was created during the brainstorming session. Verify before starting.

---

### Task 1: Verify branch state

**Files:** none modified

- [ ] **Step 1: Confirm branch and clean state**

Run:
```bash
cd "/Users/julianleitersdorf/Desktop/Coding Projects/Tarra"
git branch --show-current
git status
```
Expected: `julians-initialize` and a working tree clean (or only the committed spec from the brainstorming session).

- [ ] **Step 2: Confirm starting files exist**

Run:
```bash
ls main.py .replit templates/index.html test_basic_pitch.py pyproject.toml
```
Expected: all listed, no errors.

---

### Task 2: De-Replit

**Files:**
- Delete: `.replit`
- Modify: `pyproject.toml`

- [ ] **Step 1: Delete .replit**

Run:
```bash
rm .replit
```

- [ ] **Step 2: Rename pyproject project name**

Edit `pyproject.toml`. Replace:
```toml
name = "python-template"
```
with:
```toml
name = "tarra"
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "Remove Replit config; rename project to tarra"
```

---

### Task 3: Create `src/` layout and move app

**Files:**
- Create: `src/app.py` (from `main.py`)
- Create: `src/templates/index.html` (from `templates/index.html`)
- Delete: `main.py`, `templates/index.html`, `templates/` (empty after)

- [ ] **Step 1: Create src/ and move app**

Run:
```bash
mkdir -p src/templates
git mv main.py src/app.py
git mv templates/index.html src/templates/index.html
rmdir templates
```

- [ ] **Step 2: Verify no code references inside app.py need rewriting**

Run:
```bash
grep -n "from main\|import main\|'main:" src/app.py || echo "OK — no self-references"
```
Expected: `OK — no self-references`. (Flask's `Flask(__name__)` resolves the template folder relative to the module, so the move is sufficient — no path code change needed.)

- [ ] **Step 3: Verify app runs**

Install deps if needed (`poetry install` or `pip install flask`), then:
```bash
flask --app src.app run --port 5050
```
In another shell or browser, hit `http://127.0.0.1:5050/`. Expected: HTML loads (the index page). Ctrl-C to stop.

If `ModuleNotFoundError: No module named 'src'`, ensure you're running from the repo root. The `src.app` form requires Python to find `src/` as a package; if Flask complains, fall back to `flask --app src/app.py run --port 5050`.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Move app and templates into src/ layout"
```

---

### Task 4: Move test file into tests/

**Files:**
- Create: `tests/test_basic_pitch.py` (from `test_basic_pitch.py`)
- Delete: `test_basic_pitch.py`

- [ ] **Step 1: Move test file**

Run:
```bash
mkdir -p tests
git mv test_basic_pitch.py tests/test_basic_pitch.py
```

- [ ] **Step 2: Check for stale imports**

Run:
```bash
grep -n "from main\|import main" tests/test_basic_pitch.py || echo "OK — no main imports"
```
Expected: `OK — no main imports`. (The file is a standalone script that only imports `os`, `sys`, and basic-pitch directly; no fixes needed.)

- [ ] **Step 3: Run the test to confirm it still works**

Run:
```bash
python tests/test_basic_pitch.py
```
Expected: same output as before the move. If basic-pitch isn't installed, the script will exit gracefully with a message — that's fine, this isn't being fixed in this branch (it's a tech-debt seed entry).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Move test_basic_pitch.py into tests/"
```

---

### Task 5: Verify .gitignore handles uploads/

**Files:**
- Modify: `.gitignore` (only if needed)

- [ ] **Step 1: Check current .gitignore**

Run:
```bash
grep -n "uploads" .gitignore || echo "MISSING"
```

- [ ] **Step 2: If MISSING, append uploads/ rule**

If the previous step printed `MISSING`, append to `.gitignore`:
```
# Runtime upload directory (created at app start)
uploads/
```
Otherwise skip this step.

- [ ] **Step 3: Commit if changed**

```bash
git status
# If .gitignore changed:
git add .gitignore
git commit -m "Ignore runtime uploads/ directory"
```
If no change, skip the commit.

---

### Task 6: Write starter CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write the starter CLAUDE.md**

Create `CLAUDE.md` with the following content:

```markdown
# Tarra

Tarra is a guitar-teacher web app. Audio gets uploaded, Basic Pitch turns it into a list of notes, and the app uses that to teach.

Developer: Ilai. High school student, migrating this project from Replit to Claude Code.

---

## Onboarding mode

If `JULIANS-HELP/` exists in this repo, **you are in onboarding mode.** Do not start coding work, do not propose features, do not refactor.

Instead:
1. Read `JULIANS-HELP/00-START-HERE.md`
2. Follow the steps it lays out, in order
3. The final step (`03-finalize.md`) will replace this CLAUDE.md with a real one and delete `JULIANS-HELP/`

Tone for the entire onboarding conversation: **calm, brief, dry.** Ilai is a smart kid; one or two sentences is enough. No cheerleading, no exclamation marks, no emoji confetti. Light humor is fine.

If `JULIANS-HELP/` does not exist, this file should have been replaced — proceed normally with whatever Ilai asks.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "Add starter CLAUDE.md (self-replacing during onboarding)"
```

---

### Task 7: Write README.md placeholder

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

Create `README.md` with:

```markdown
# Tarra

Guitar-teacher web app. Upload a recording, get back the notes that were played.

## Run it

```
flask --app src.app run
```

Open http://127.0.0.1:5000

## Project structure

- `src/app.py` — Flask app and routes
- `src/templates/` — HTML templates
- `tests/` — test scripts
- `docs/` — architecture, ideas, specs, tech debt
- `uploads/` — runtime upload directory (gitignored)

*(This README will be filled out more during onboarding.)*
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "Add README placeholder"
```

---

### Task 8: Write ROADMAP.md skeleton

**Files:**
- Create: `ROADMAP.md`

- [ ] **Step 1: Write ROADMAP.md**

Create `ROADMAP.md` with:

```markdown
# Roadmap

A snapshot of what's built, what's next, and what's later. Update as you go.

## Now (built and working)

*(Filled in during onboarding.)*

## Next (actively working on)

*(Filled in during onboarding.)*

## Later (ideas you want to get to)

*(Filled in during onboarding. Raw ideas go in `docs/ideas/` first; they graduate here when you're ready to commit to them.)*
```

- [ ] **Step 2: Commit**

```bash
git add ROADMAP.md
git commit -m "Add ROADMAP skeleton"
```

---

### Task 9: Write docs/ skeleton

**Files:**
- Create: `docs/architecture.md`
- Create: `docs/ideas/README.md`
- Create: `docs/specs.md`
- Create: `docs/tech-debt.md`

- [ ] **Step 1: Create docs/ subdirectories**

Run:
```bash
mkdir -p docs/ideas
```

- [ ] **Step 2: Write docs/architecture.md**

Create `docs/architecture.md` with:

```markdown
# Architecture

How the pieces of Tarra fit together.

*(Filled in during onboarding. The intake will ask you to walk through the front-end, the Flask back-end, Basic Pitch, and what happens when a file is uploaded — and the answers go here.)*
```

- [ ] **Step 3: Write docs/ideas/README.md**

Create `docs/ideas/README.md` with:

```markdown
# Ideas

Drop one file in here per raw feature idea — "what if Tarra could detect tuning automatically" kind of thing. Low ceremony, no template required.

When an idea gets serious enough to build, graduate it to a section in `../specs.md` and move it from "Later" to "Next" in `../../ROADMAP.md`.
```

- [ ] **Step 4: Write docs/specs.md**

Create `docs/specs.md` with:

```markdown
# Specs

Before building a feature, write a short section here. Each section answers three questions:

- **What** are you building?
- **Why** — what problem does it solve?
- **Done means** — how do you know it works?

Append new sections at the bottom. Older sections stay (they're a record).

---

## Example: Audio upload (already built)

**What:** A page where the user picks an `.mp3` or `.wav` file and uploads it.

**Why:** Tarra needs an audio recording to analyze before it can teach anything.

**Done means:** A 10 MB or smaller `.mp3`/`.wav` uploads successfully, gets saved to `uploads/`, and returns a 200 response with the filename. Files outside that get rejected with a clear message.

---

*(Add more sections below as you build features.)*
```

- [ ] **Step 5: Write docs/tech-debt.md**

Create `docs/tech-debt.md` with:

```markdown
# Tech debt

Running list of things that work but are hacky, fragile, or worth fixing later. Append bullets with a date. Don't fix everything — just track it so it doesn't slip your mind.

---

- **2026-05-19** — `basic-pitch` is imported in `src/app.py` but isn't listed in `pyproject.toml` as a dependency. If someone clones the repo and installs deps, the import will silently fail and the app will run in fallback mode (no actual note detection). Fix: add `basic-pitch = "^X.Y"` to `pyproject.toml` with the real version, then `poetry lock`.
```

- [ ] **Step 6: Commit**

```bash
git add docs/architecture.md docs/ideas/ docs/specs.md docs/tech-debt.md
git commit -m "Add docs/ skeleton (architecture, ideas, specs, tech-debt)"
```

---

### Task 10: Write JULIANS-HELP/00-START-HERE.md

**Files:**
- Create: `JULIANS-HELP/00-START-HERE.md`

- [ ] **Step 1: Create JULIANS-HELP/ and write entry file**

Run:
```bash
mkdir -p JULIANS-HELP
```

Create `JULIANS-HELP/00-START-HERE.md` with:

```markdown
# Start here (for Claude)

Hello — this is the entry point for Ilai's first onboarding session on Tarra.

## Tone (important — applies to everything that follows)

Calm, brief, dry. Ilai is a smart high school student; one or two sentences is enough for any explanation. No cheerleading, no exclamation marks for emphasis, no emoji confetti. Light humor is fine. If you'd say something with a "!", say it with a "." instead.

## What you're doing

You're walking Ilai through onboarding to Claude Code on his Tarra project. Four steps, in order:

1. **Intake** — read `01-intake.md`, follow it. You'll be asking Ilai questions and writing his answers into the right doc files as you go.
2. **Setup** — read `02-setup.md`, follow it. File-relocation map first, then plugin install, then brief concept paragraphs.
3. **Finalize** — read `03-finalize.md`, follow it. This step is destructive (deletes this folder, rewrites `CLAUDE.md`). Confirm with Ilai before doing it.
4. **Submission note** — `SCHOOL-SUBMISSION-NOTE.md` is for Ilai's reference if he ever needs it. You don't need to act on it.

## Rules

- One step at a time. Finish a step before moving on.
- Confirm with Ilai before writing to any doc file — read your draft back, ask "look right?", then save.
- Keep his words. If he describes something in his own way, write it that way. Don't translate his explanations into engineering-speak.
- Don't propose features, refactors, or improvements during onboarding. Capture, don't redesign.

Start by reading `01-intake.md`.
```

- [ ] **Step 2: Commit**

```bash
git add JULIANS-HELP/00-START-HERE.md
git commit -m "Add JULIANS-HELP/00-START-HERE entry point"
```

---

### Task 11: Write JULIANS-HELP/01-intake.md

**Files:**
- Create: `JULIANS-HELP/01-intake.md`

- [ ] **Step 1: Write the intake script**

Create `JULIANS-HELP/01-intake.md` with:

```markdown
# Intake (for Claude)

Walk Ilai through these questions in order. After each one, draft what you'll write, read it back, confirm, then save to the indicated file.

Greeting: introduce yourself in one line. Something like: *"Hey Ilai — Julian set this branch up so we can get Tarra running on Claude Code and get your docs in shape. Should take ~15 minutes. Going to ask you a few things, then we'll do setup."*

---

## 1. Project description

Ask: *"What does Tarra do? Explain it like you'd tell a friend who's never seen it."*

→ Writes to: `README.md` (update the first section under `# Tarra`).
→ Keep his language. One paragraph is plenty.

## 2. Code walkthrough → architecture

Say: *"Walk me through how the pieces fit together. Front-end, the Flask back-end in `src/app.py`, Basic Pitch, and what happens when a user uploads a file. I'll write it up as we go."*

→ Writes to: `docs/architecture.md`.
→ Structure as four short sections: **Front-end**, **Back-end (Flask)**, **Basic Pitch**, **Upload flow (end-to-end)**. One short paragraph each, in his words.
→ If he gets stuck on a piece, offer to read the relevant code yourself and ask him to confirm your summary. Don't lecture.

## 3. What's working

Ask: *"What's already built that you're happy with? Features that work the way you wanted."*

→ Writes to: `ROADMAP.md` under **Now (built and working)**.
→ One bullet per feature, his words.

## 4. What's in flight

Ask: *"What are you actively working on right now, or about to start?"*

→ Writes to: `ROADMAP.md` under **Next (actively working on)**.
→ One bullet per item.

## 5. Wishlist

Ask: *"What features do you wish were in there? Stuff you'd add if you had time, no constraints."*

→ Each idea: one file in `docs/ideas/`, filename like `auto-tuning-detection.md`. Inside: one short paragraph.
→ Also add a one-line bullet to `ROADMAP.md` under **Later**.

## 6. What's shaky

Ask: *"What feels hacky or fragile right now? Stuff you wrote that works but you're not proud of, or that you're worried might break."*

→ Writes to: `docs/tech-debt.md`. Append bullets, each prefixed with today's date.
→ If he says "nothing comes to mind," that's fine. Move on.

---

When all six are done, tell Ilai: *"Intake done. Want to move on to setup?"* and read `02-setup.md`.
```

- [ ] **Step 2: Commit**

```bash
git add JULIANS-HELP/01-intake.md
git commit -m "Add JULIANS-HELP/01-intake script"
```

---

### Task 12: Write JULIANS-HELP/02-setup.md

**Files:**
- Create: `JULIANS-HELP/02-setup.md`

- [ ] **Step 1: Write the setup script**

Create `JULIANS-HELP/02-setup.md` with:

```markdown
# Setup (for Claude)

Two parts: tell Ilai where his files moved, then help him install plugins. Keep the two short paragraphs at the end ready to surface if relevant later in the conversation — they're not a lecture.

---

## Part 1: Where your code went

Show Ilai this table verbatim:

```
Heads up — your code moved when this branch was set up. Nothing about
the code itself changed, just where things live.

  main.py                  →  src/app.py
  templates/index.html     →  src/templates/index.html
  test_basic_pitch.py      →  tests/test_basic_pitch.py
  .replit                  →  deleted (you're on Claude Code now,
                              not Replit)

To run it:
  flask --app src.app run

Open http://127.0.0.1:5000 in your browser. Same as before, just a
different command.
```

Ask: *"Want to try running it now to make sure it works?"* If yes, walk him through running the command and hitting the URL. If something fails, debug with him.

## Part 2: Plugins

Tell him: *"Going to install the `superpowers` plugin. It's a set of tools that make Claude better at planning and reviewing code — Julian uses it. Takes a minute."*

Then walk him through:

1. Open Claude Code's plugin manager (`/plugins` slash command in Claude Code).
2. Search for or paste the GitHub URL: `obra/superpowers`.
3. Install. Confirm it loaded by running `/help` and looking for superpowers-related skills in the list.

If the install fails, fall back to the manual instructions at `https://github.com/obra/superpowers#readme`.

---

## Part 3: Two concepts (use only if/when they come up)

Don't dump these on Ilai. Surface them in passing once each, if a natural moment appears later in the session. Keep them this short:

**TDD.** *"One thing as we work — when you want a new function, it's often worth writing the test first (a small script that calls it and checks the answer). Tells you immediately if your code does what you said it would. I'll usually offer it; you can say yes or no."*

**Agents in parallel.** *"Sometimes a task has steps that depend on each other — do A, then B using A's result. Sometimes the steps are independent. When they're independent, I can dispatch a few in parallel — faster. I'll just do it when it makes sense; no need to think about it."*

That's it. If the moment doesn't come, don't force them. They're not the point of onboarding.

---

When setup is done, tell Ilai: *"Setup done. Last step is graduating this branch — want to do that now?"* and read `03-finalize.md`.
```

- [ ] **Step 2: Commit**

```bash
git add JULIANS-HELP/02-setup.md
git commit -m "Add JULIANS-HELP/02-setup script"
```

---

### Task 13: Write JULIANS-HELP/03-finalize.md

**Files:**
- Create: `JULIANS-HELP/03-finalize.md`

- [ ] **Step 1: Write the finalize script**

Create `JULIANS-HELP/03-finalize.md` with:

```markdown
# Finalize (for Claude)

This step is destructive: replaces `CLAUDE.md` with a real one and deletes `JULIANS-HELP/`. Confirm with Ilai before doing it.

## Confirmation prompt

Say to Ilai, verbatim or close:

*"Ready to graduate this branch? Here's what'll happen:*

1. *I'll write a fresh `CLAUDE.md` based on what you told me during intake — project description, how to run it, where docs live, conventions.*
2. *I'll delete this `JULIANS-HELP/` folder. It's done its job.*
3. *I'll commit both changes with the message 'Onboarding complete — graduate to real CLAUDE.md'.*

*After that you're on a clean branch and can merge into main when you're ready. If you hate the result, the commit is easy to revert. Want to go?"*

Wait for explicit yes.

## On confirmation, do this

1. **Rewrite `/CLAUDE.md`** from scratch. Template:

```markdown
# Tarra

[One-paragraph description of Tarra in Ilai's own words, lifted from the intake answer to question 1.]

## Run it

```
flask --app src.app run
```

Open http://127.0.0.1:5000

## Project structure

- `src/app.py` — Flask app and routes
- `src/templates/` — HTML templates
- `tests/` — test scripts
- `docs/architecture.md` — how the pieces fit together
- `docs/specs.md` — feature specs, append-only
- `docs/ideas/` — raw feature wishlist
- `docs/tech-debt.md` — things to fix later
- `ROADMAP.md` — Now / Next / Later

## Working with Claude

[Anything Ilai mentioned during intake about how he likes to work — e.g., "Ilai likes to see test output before merging," or "Ilai is still learning Flask, so explain Flask-specific concepts when they come up." If nothing came up, omit this section entirely.]

## Domain notes

- **Basic Pitch** is Spotify's open-source library that turns audio into MIDI notes. It's the core of Tarra's note detection.
- [Any other domain terms Ilai used that would help a future Claude session.]
```

2. **Delete the JULIANS-HELP folder:**

```bash
git rm -r JULIANS-HELP/
```

3. **Commit:**

```bash
git add CLAUDE.md
git commit -m "Onboarding complete — graduate to real CLAUDE.md"
```

4. **Tell Ilai:** *"Done. Branch is clean, ready to merge into main when you want. Want me to do that now, or hold off?"*

If yes, run:
```bash
git checkout main
git merge julians-initialize
git branch -d julians-initialize
```
```

- [ ] **Step 2: Commit**

```bash
git add JULIANS-HELP/03-finalize.md
git commit -m "Add JULIANS-HELP/03-finalize script"
```

---

### Task 14: Write JULIANS-HELP/SCHOOL-SUBMISSION-NOTE.md

**Files:**
- Create: `JULIANS-HELP/SCHOOL-SUBMISSION-NOTE.md`

- [ ] **Step 1: Write the submission note**

Create `JULIANS-HELP/SCHOOL-SUBMISSION-NOTE.md` with:

```markdown
# School submission note

For Ilai's reference. Claude doesn't need to act on this.

This branch (`julians-initialize`) added some one-time scaffolding to help migrate Tarra from Replit to Claude Code. Once onboarding finishes:

- The `JULIANS-HELP/` folder is gone.
- The starter `CLAUDE.md` is replaced with a real one.
- The branch is ready to merge into `main`.

After the merge, the project state is clean — no trace of the scaffolding in the working tree.

If your teacher will look at the git **history** (commits, not just files):

- The scaffolding shows up across a handful of commits with messages like "Add JULIANS-HELP/..." and a final "Onboarding complete — graduate to real CLAUDE.md."
- If that's weird for your submission, you can squash the whole branch into one commit before merging:
  ```
  git checkout julians-initialize
  git reset --soft main
  git commit -m "Project setup"
  ```
- Or just delete the branch's history entirely after merging:
  ```
  git branch -d julians-initialize
  ```

If your teacher only looks at the final code (most common), you don't need to do anything.
```

- [ ] **Step 2: Commit**

```bash
git add JULIANS-HELP/SCHOOL-SUBMISSION-NOTE.md
git commit -m "Add school submission note for Ilai"
```

---

### Task 15: Final verification and push

**Files:** none modified

- [ ] **Step 1: Confirm the final tree**

Run:
```bash
find . -type f -not -path './.git/*' -not -path './uploads/*' -not -path './__pycache__/*' -not -path '*/\.*' | sort
```

Expected output should include (at minimum):
```
./.gitignore
./CLAUDE.md
./JULIANS-HELP/00-START-HERE.md
./JULIANS-HELP/01-intake.md
./JULIANS-HELP/02-setup.md
./JULIANS-HELP/03-finalize.md
./JULIANS-HELP/SCHOOL-SUBMISSION-NOTE.md
./README.md
./ROADMAP.md
./docs/architecture.md
./docs/ideas/README.md
./docs/specs.md
./docs/superpowers/plans/2026-05-19-julians-initialize.md
./docs/superpowers/specs/2026-05-19-julians-initialize-design.md
./docs/tech-debt.md
./poetry.lock
./pyproject.toml
./src/app.py
./src/templates/index.html
./tests/test_basic_pitch.py
```

No `.replit`, no `main.py` at root, no `templates/` at root.

- [ ] **Step 2: Confirm app still runs**

```bash
flask --app src.app run --port 5050
```
Hit `http://127.0.0.1:5050/`. Expect the index page. Ctrl-C.

- [ ] **Step 3: Confirm test still runs**

```bash
python tests/test_basic_pitch.py
```
Expect: same behavior as before the move (works if basic-pitch is installed, exits cleanly if not).

- [ ] **Step 4: Confirm clean git status**

```bash
git status
```
Expected: working tree clean, on branch `julians-initialize`.

- [ ] **Step 5: Push the branch**

```bash
git push -u origin julians-initialize
```

- [ ] **Step 6: Confirm with Julian**

Tell Julian the branch is pushed. He can now share it with Ilai, who checks it out and opens Claude Code to start onboarding.

---

## Self-review notes

Done after writing. Spec coverage check:

- Phase 1 de-Replit: Task 2 ✓
- Phase 1 refactor: Tasks 3, 4 ✓
- Phase 1 verify runs: Tasks 3.3, 4.3, 15.2, 15.3 ✓
- Phase 1 docs scaffolding: Tasks 6–9 ✓
- Phase 1 JULIANS-HELP/: Tasks 10–14 ✓
- Phase 1 commit + push: Task 15 ✓
- Phase 2: out of scope (executed by Ilai's session). Plan does not implement it.

No placeholders, no "TBD". Tech debt seed entry uses `^X.Y` as the version placeholder for Ilai to fill in — that's intentional (he looks up the real version when he fixes it).
