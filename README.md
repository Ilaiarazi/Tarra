# Tarra

Tarra is a learning assistant and toolkit for guitar. You upload a video of yourself playing, and it critiques your accuracy. For improvisation, it suggests scales that fit the tune, tells you the chords being used, and gives you ideas for what to play over them. It's mainly aimed at lead guitar — essentially a practice coach. Under the hood it uses Basic Pitch (Spotify's pitch detection tool) to pull notes out of your audio.

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
