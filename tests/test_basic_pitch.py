# test_basic_pitch.py
# ─────────────────────────────────────────────────────────────────────────────
# Run this in the Replit Shell with:
#   python3 test_basic_pitch.py
#
# Or point it at a specific file:
#   python3 test_basic_pitch.py uploads/my_recording.wav
# ─────────────────────────────────────────────────────────────────────────────

import os    # lets us check if files/folders exist and build file paths
import sys   # lets us exit the script early (sys.exit) and read command-line arguments


# ── Step 1: Find an audio file to test with ──────────────────────────────────

UPLOADS_FOLDER = 'uploads'
# This is the folder where files land when someone uploads through the website.

def find_test_file():
    """
    Looks inside the 'uploads' folder for any audio file.
    Returns the full path to the first one it finds.
    If nothing is there it tells the user what to do and stops.
    """
    # os.path.exists() returns True if the folder is there, False if not.
    if not os.path.exists(UPLOADS_FOLDER):
        print("❌  No 'uploads' folder found.")
        print("    Upload an audio file through the Tarra website first.")
        sys.exit(1)  # stop the script with exit code 1 (means something went wrong)

    # os.listdir() returns a list of every filename inside the folder.
    for filename in os.listdir(UPLOADS_FOLDER):
        # .lower() makes the check case-insensitive (e.g. 'Song.WAV' still works)
        if filename.lower().endswith(('.wav', '.mp3')):
            # os.path.join() builds 'uploads/my_song.wav' safely on any OS
            return os.path.join(UPLOADS_FOLDER, filename)

    print("❌  No audio file found in uploads/.")
    print("    Upload an MP3 or WAV file through the Tarra website first.")
    sys.exit(1)


# ── Step 2: Convert MIDI numbers to human-readable note names ────────────────

# Basic Pitch describes every detected pitch as a MIDI note number.
# MIDI is a universal music standard: 60 = Middle C, 61 = C#4, 62 = D4, etc.
# Each step up is one semitone — the same as one fret up on a guitar.
# The number goes from 0 (very low, below a bass guitar) to 127 (very high).

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
# This list has 12 items — one for each semitone in an octave.
# Index 0 = C, index 1 = C#, ..., index 11 = B.

def midi_to_note_name(midi_number):
    """
    Converts a MIDI number into something like 'E4' or 'A2'.
    
    Example: midi_number = 64
      64 % 12 = 4  →  NOTE_NAMES[4] = 'E'
      64 // 12 = 5, 5 - 1 = 4  →  octave 4
      Result: 'E4'  (the open top E string on a guitar)
    """
    note_letter = NOTE_NAMES[midi_number % 12]
    # % 12 gives the remainder when divided by 12,
    # which tells us which of the 12 notes it is within its octave.

    octave = (midi_number // 12) - 1
    # // 12 does integer division (no decimal), giving us the octave number.
    # We subtract 1 because of how MIDI numbers are defined
    # (MIDI 0 is C in octave -1, MIDI 12 is C0, MIDI 60 is C4, etc.).

    return f"{note_letter}{octave}"
    # f"..." is an f-string — it puts variables directly into a string.
    # e.g. note_letter='E', octave=4  →  'E4'


# ── Step 3: Guitar string reference ──────────────────────────────────────────

# This dictionary maps common MIDI numbers to their guitar string names.
# Useful for telling the player which string a note came from.
GUITAR_STRINGS = {
    40: 'Low E string (open)',   # thickest string, lowest pitch
    45: 'A string (open)',
    50: 'D string (open)',
    55: 'G string (open)',
    59: 'B string (open)',
    64: 'High E string (open)',  # thinnest string, highest pitch
}

def guess_guitar_string(midi_number):
    """
    Returns a rough guess of which guitar string area this note is in.
    Not exact (players can play the same pitch on different strings),
    but gives a helpful hint.
    """
    if midi_number <= 43:
        return 'low E / A area'
    elif midi_number <= 52:
        return 'A / D area'
    elif midi_number <= 57:
        return 'D / G area'
    elif midi_number <= 62:
        return 'G / B area'
    else:
        return 'B / high E area'


# ── Step 4: Run Basic Pitch and print the results ────────────────────────────

def analyse_audio(filepath):
    """
    Loads the audio file, runs Basic Pitch AI on it,
    then prints every detected note in a readable table.
    """

    print(f"\n🎸  Analysing: {filepath}")
    print("    Loading Basic Pitch model — this takes 15–30 seconds on first run...\n")

    # We import Basic Pitch inside the function rather than at the top of the file.
    # This way, if it's not installed, the error message appears here with
    # a helpful hint, rather than as a confusing crash at startup.
    try:
        from basic_pitch.inference import predict
        # predict() is the main function — it does all the AI heavy lifting.

        from basic_pitch import ICASSP_2022_MODEL_PATH
        # ICASSP_2022_MODEL_PATH is the path to the pre-trained AI model file
        # that ships inside the basic-pitch package.
        # ICASSP is the name of the research conference where Basic Pitch was published.

    except ImportError:
        # ImportError means Python couldn't find the package.
        print("❌  basic-pitch is not installed.")
        print("    Run this in the Replit Shell:")
        print("        pip install basic-pitch")
        sys.exit(1)

    # Now run the actual analysis.
    try:
        model_output, midi_data, note_events = predict(
            filepath,               # path to the audio file
            ICASSP_2022_MODEL_PATH  # which AI model to use
        )
        # predict() returns three things:
        #   model_output  — raw numbers from the neural network (we won't use these directly)
        #   midi_data     — the results as a MIDI file object (digital sheet music)
        #   note_events   — a plain list of notes, easiest to work with

    except Exception as e:
        # Exception catches any error that happens during analysis —
        # corrupted file, wrong format, etc.
        print(f"❌  Could not analyse the file.")
        print(f"    Reason: {e}")
        sys.exit(1)

    # ── Print a table of every detected note ─────────────────────────────────

    total_notes = len(note_events)
    # len() counts how many items are in the list.

    print(f"✅  Done! Basic Pitch detected {total_notes} notes.\n")

    if total_notes == 0:
        print("    No notes were found. The recording might be silent or very noisy.")
        sys.exit(0)  # exit cleanly (0 = success, no errors)

    # Print the table header
    print(f"  {'#':<5}{'Note':<7}{'Start':<10}{'End':<10}{'Duration':<11}{'Confidence':<12}{'String area'}")
    print("  " + "─" * 68)

    for i, note in enumerate(note_events):
        # note is a tuple: (start_time, end_time, pitch_midi, amplitude, pitch_bends)
        # We access each part by index:

        start_s    = note[0]   # when the note starts, in seconds from the beginning
        end_s      = note[1]   # when the note ends, in seconds
        pitch_midi = note[2]   # MIDI note number (integer, e.g. 64)
        amplitude  = note[3]   # confidence / loudness, from 0.0 (none) to 1.0 (certain)

        duration   = end_s - start_s
        # How long the note lasts. 0.25 seconds = roughly a 16th note at 120 BPM.

        note_name  = midi_to_note_name(pitch_midi)
        # e.g. 64 → 'E4'

        confidence = f"{amplitude * 100:.0f}%"
        # amplitude is 0.0–1.0, so ×100 gives a percentage.
        # :.0f means 'format as a float with 0 decimal places' (i.e. a whole number).

        string_area = guess_guitar_string(pitch_midi)

        print(f"  {i+1:<5}{note_name:<7}{start_s:.2f}s{'':<5}{end_s:.2f}s{'':<5}{duration:.2f}s{'':<7}{confidence:<12}{string_area}")
        # :<5 means 'left-align within 5 characters' — keeps the columns neat.
        # :.2f means 'format as a float with 2 decimal places' (e.g. 1.35).

    # ── Print a musical summary ───────────────────────────────────────────────

    print("\n" + "─" * 70)
    print("📊  Musical Summary")
    print("─" * 70)

    # Collect every unique note name (removing duplicates with set())
    all_note_names  = [midi_to_note_name(n[2]) for n in note_events]
    # This is a list comprehension — a compact way to build a list.
    # For every note n in note_events, call midi_to_note_name on its pitch.

    unique_notes    = sorted(set(all_note_names))
    # set() removes duplicates. sorted() puts them in alphabetical order.

    avg_confidence  = sum(n[3] for n in note_events) / total_notes
    # sum() adds up all the amplitude values. Divide by total to get the average.

    recording_length = note_events[-1][1]
    # note_events[-1] is the last note. [1] is its end time.
    # So this is how long the whole recording is (in seconds).

    # Notes per second tells us roughly how fast the playing is
    notes_per_second = total_notes / recording_length if recording_length > 0 else 0

    print(f"  Total notes detected   : {total_notes}")
    print(f"  Unique pitches used    : {', '.join(unique_notes)}")
    print(f"  Recording length       : {recording_length:.1f} seconds")
    print(f"  Notes per second       : {notes_per_second:.1f}  (higher = faster playing)")
    print(f"  Average confidence     : {avg_confidence * 100:.0f}%")
    print()

    # Interpret the confidence score for the beginner
    if avg_confidence >= 0.7:
        print("  🟢  High confidence — notes were clear and well-defined.")
    elif avg_confidence >= 0.4:
        print("  🟡  Medium confidence — some notes were unclear (bends, muted strings, noise?).")
    else:
        print("  🔴  Low confidence — recording may have background noise or tuning issues.")

    print()
    print("  What the columns mean:")
    print("  • Note       — the musical note name (e.g. E4 = open top E string)")
    print("  • Start/End  — timestamps in seconds from the beginning of the recording")
    print("  • Duration   — how long the note was held")
    print("  • Confidence — how certain Basic Pitch is that this note was really played")
    print("  • String area — rough guess of which guitar string region the note is in")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # __name__ == '__main__' is True only when you run this file directly.
    # If another script imported this file, it would be False and this block
    # would be skipped — which is the correct behaviour.

    if len(sys.argv) > 1:
        # sys.argv is a list of command-line arguments.
        # sys.argv[0] is always the script name itself.
        # sys.argv[1] would be the first argument the user typed after it.
        # e.g.  python3 test_basic_pitch.py uploads/song.wav
        #       sys.argv[1] = 'uploads/song.wav'
        audio_path = sys.argv[1]

        if not os.path.exists(audio_path):
            print(f"❌  File not found: {audio_path}")
            sys.exit(1)
    else:
        # No argument given — find the first audio file in uploads/
        audio_path = find_test_file()

    analyse_audio(audio_path)
