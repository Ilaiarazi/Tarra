# Tech debt

Running list of things that work but are hacky, fragile, or worth fixing later. Append bullets with a date. Don't fix everything — just track it so it doesn't slip your mind.

---

- **2026-05-19** — `basic-pitch` is imported in `src/app.py` but isn't listed in `pyproject.toml` as a dependency. If someone clones the repo and installs deps, the import will silently fail and the app will run in fallback mode (no actual note detection). Fix: add `basic-pitch = "^X.Y"` to `pyproject.toml` with the real version, then `poetry lock`.
- **2026-05-22** — Not sure how good Basic Pitch actually is at detecting guitar notes. Works, but accuracy hasn't been properly tested.
