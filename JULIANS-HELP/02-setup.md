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
