# Tarra

Tarra is a learning assistant and toolkit for guitar. You upload a video of yourself playing, and it critiques your accuracy. For improvisation, it suggests scales that fit the tune, tells you the chords being used, and gives you ideas for what to play over them. It's mainly aimed at lead guitar — essentially a practice coach. Under the hood it uses Basic Pitch (Spotify's pitch detection tool) to pull notes out of your audio.

## Run it

```
python3.11 -m flask --app src.app run --port 5001
```

Open http://127.0.0.1:5001

(Port 5000 is taken by macOS AirPlay. Use 5001.)

## Project structure

- `src/app.py` — Flask app and routes
- `src/templates/` — HTML templates
- `tests/` — test scripts
- `docs/architecture.md` — how the pieces fit together
- `docs/specs.md` — feature specs, append-only
- `docs/ideas/` — raw feature wishlist
- `docs/tech-debt.md` — things to fix later
- `ROADMAP.md` — Now / Next / Later

## Domain notes

- **Basic Pitch** is Spotify's open-source library that turns audio into MIDI notes. It's the core of Tarra's note detection. Accuracy on guitar hasn't been fully tested yet.
- The app accepts audio (MP3, WAV) and video (MOV, MP4, M4A, etc.). For video, the audio track is extracted to a temp WAV with ffmpeg — bundled via the `imageio-ffmpeg` package, so no system ffmpeg install is needed — before Basic Pitch runs. See `extract_audio()` in `src/app.py`. Upload limit is 200 MB.
- Note names like "E4" (MIDI pitch notation) are considered confusing for non-musicians — prefer plain language in the UI where possible.
