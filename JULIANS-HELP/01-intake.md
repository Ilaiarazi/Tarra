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
