# Roadmap

A snapshot of what's built, what's next, and what's later. Update as you go.

## Now (built and working)

- Upload pipeline works end-to-end: submit a recording, Basic Pitch analyzes it, results come back
- Audio **and video** upload — including video straight from an iPhone camera roll; the audio track is extracted with ffmpeg before analysis
- Landing page: Stratocaster hero, editorial redesign (Bricolage Grotesque type), scroll progress
- Results dashboard on its own page with tabs: Overview, Timing, Solo Ideas, Scales, Chords
- AI coach feedback, scale suggestions, and solo ideas via the Claude API
- Chord chart generator (CAGED movable shapes, every position up the neck)
- User accounts: sign up / log in, with every analysis saved to a browsable history

## Next (actively working on)

- Generate written feedback from the note data (not just raw numbers)
- Polish the results page — better UI for displaying feedback
- Error handling and edge cases
- Move the results dashboard to its own page (not on the landing page)

## Later (ideas you want to get to)

- Feedback dashboard: bend accuracy, phrasing quality, timing
- Scale and mode charts based on detected notes
- Solo idea generator — outputs a guitar tab of things that would work over the tune
- Guitar body background on landing page (Stratocaster or Les Paul shape)
- Real-time practice mode — live note-by-note feedback via microphone
- Shareable result cards for social media
- Streak tracker (Duolingo-style daily practice habit)
- Similarity score vs a reference track
- Source separation (Demucs) — isolate lead guitar from a mixed recording before analysis
