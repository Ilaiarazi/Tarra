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
