# Architecture

How the pieces of Tarra fit together.

## Front-end

Right now it's a landing page with a file upload field. The plan is to add user accounts so people can log in and see a history of all their videos and the feedback Tarra's given them.

## Back-end (Flask)

`src/app.py` handles two routes: the home page and the upload endpoint. When a file comes in it validates the extension (MP3 or WAV only, no video yet), saves it to the `uploads/` folder, and hands it off to Basic Pitch. Results come back as JSON.

## Basic Pitch

Spotify's pitch detection tool, already integrated. It loads at startup so the model is in memory before any requests come in. Given an audio file, it returns a list of note events — each one has a start time, end time, pitch, confidence score, and pitch bend data. The app converts pitches to readable note names (like "E4") and roughly maps them to guitar string regions.

## Upload flow (end-to-end)

User submits an audio file → Flask validates and saves it → Basic Pitch analyzes it → the app builds a note list plus a summary (total notes, unique notes, average confidence, recording length, notes per second) → all of it returns to the front-end as JSON.
