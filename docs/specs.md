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
