import os
from dotenv import load_dotenv
load_dotenv(override=True)

import anthropic
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# ── Try to load Basic Pitch once at startup ───────────────────────────────────
# We import it here (at the top) so the AI model loads into memory when
# gunicorn starts, rather than on every request. This makes the first
# analysis much faster.
try:
    from basic_pitch.inference import predict as bp_predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    BASIC_PITCH_READY = True   # flag we can check later
except ImportError:
    BASIC_PITCH_READY = False  # basic-pitch not installed — graceful fallback

app = Flask(__name__)

# ── Upload settings ───────────────────────────────────────────────────────────
UPLOAD_FOLDER     = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
MAX_FILE_SIZE     = 10 * 1024 * 1024   # 10 MB in bytes

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


# ── Helper: MIDI number → note name ──────────────────────────────────────────
# MIDI numbers are integers (0–127) that represent musical pitches.
# 60 = Middle C, 69 = A4 (concert pitch 440 Hz), 64 = E4 (open top guitar string).

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def midi_to_note_name(midi_number):
    """Convert e.g. 64 → 'E4'. Used to make output human-readable."""
    note   = NOTE_NAMES[int(midi_number) % 12]
    octave = (int(midi_number) // 12) - 1
    return f"{note}{octave}"


# ── Helper: check file extension ──────────────────────────────────────────────
def allowed_file(filename):
    """Returns True only for .mp3 and .wav files."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Helper: rough guitar string from pitch ────────────────────────────────────
def guitar_string_area(midi_number):
    """Returns a rough guess of which string region the note sits in."""
    if midi_number <= 43:   return 'Low E / A area'
    if midi_number <= 52:   return 'A / D area'
    if midi_number <= 57:   return 'D / G area'
    if midi_number <= 62:   return 'G / B area'
    return 'B / high E area'


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/results')
def results():
    return render_template('results.html')


@app.route('/solo-ideas', methods=['POST'])
def solo_ideas():
    data = request.get_json()
    key = data.get('key', 'A')
    mode = data.get('mode', 'minor')
    chords = data.get('chords', '')

    prompt = f"""You are a guitar teacher. The student is playing in {key} {mode}.
Chord progression: {chords if chords else 'not specified'}

Write 2 short guitar solo lick ideas in standard ASCII tab format. Each lick should be 1-2 bars, playable by an intermediate guitarist. Use this exact format:

Lick 1 — [brief name]
e|---|
B|---|
G|---|
D|---|
A|---|
E|---|

Lick 2 — [brief name]
e|---|
B|---|
G|---|
D|---|
A|---|
E|---|

After the tabs, add one sentence explaining what makes these licks work over this key/progression. Keep it plain English, no theory jargon."""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=600,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return jsonify({'result': message.content[0].text})
    except Exception:
        return jsonify({'error': 'Could not generate solo ideas. Please try again.'}), 500


@app.route('/scales', methods=['POST'])
def scales():
    data = request.get_json()
    key = data.get('key', 'A')
    mode = data.get('mode', 'minor')
    chords = data.get('chords', '')

    prompt = f"""You are a guitar teacher. The student is playing in {key} {mode}.
Chord progression: {chords if chords else 'not specified'}

List the 4 most useful scales for soloing over this. For each one give:
- The scale name (keep it short)
- One sentence on why it fits (plain English, no jargon)
- The notes in the scale, listed simply like: A B C D E F G

Return as a JSON array like this:
[
  {{"name": "A Natural Minor", "why": "...", "notes": "A B C D E F G"}},
  ...
]

Return only the JSON array, nothing else."""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=600,
            messages=[{'role': 'user', 'content': prompt}]
        )
        import json as json_lib, re as re_lib
        raw = message.content[0].text
        raw = re_lib.sub(r'^```(?:json)?\s*', '', raw.strip())
        raw = re_lib.sub(r'\s*```$', '', raw)
        scales_data = json_lib.loads(raw)
        return jsonify({'scales': scales_data})
    except Exception:
        return jsonify({'error': 'Could not generate scale suggestions. Please try again.'}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    s = data.get('summary', {})
    notes = data.get('notes', [])
    unique_notes = s.get('unique_notes', [])

    prompt = f"""You are a guitar coach reviewing someone's playing. Here is the note detection data from their recording:

- Recording length: {s.get('recording_length')} seconds
- Total notes detected: {s.get('total_notes')}
- Notes per second: {s.get('notes_per_second')} (playing density)
- Average detection confidence: {s.get('avg_confidence')}% ({s.get('confidence_label', '').split(' — ')[0]})
- Unique pitches used: {', '.join(unique_notes)} ({len(unique_notes)} distinct notes)

Based on this data, write 3–4 short paragraphs of plain-English coaching feedback. Cover:
1. What the notes suggest about the key or scale being used
2. What the playing density and confidence say about their technique
3. One or two specific things to work on
4. One encouraging observation

Write directly to the player. Keep it conversational — no jargon, no note names like "E4". Imagine you're a guitar teacher talking to a student after their session."""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=600,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return jsonify({'feedback': message.content[0].text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Receives the audio file, saves it, runs Basic Pitch,
    and returns the detected notes as JSON.
    The browser's fetch() call waits for this response (up to 120 seconds).
    """

    # ── Validate the incoming request ────────────────────────────────────────

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file was sent.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False,
                        'error': 'Only MP3 and WAV files are allowed.'}), 400

    # ── Save to disk ──────────────────────────────────────────────────────────

    safe_name = secure_filename(file.filename)
    # secure_filename strips dangerous characters like '..' or '/'
    # so the file can't escape the uploads folder.

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    file.save(save_path)
    # At this point the file is physically on disk at uploads/safe_name.

    # ── Run Basic Pitch ───────────────────────────────────────────────────────

    if not BASIC_PITCH_READY:
        # basic-pitch wasn't importable at startup — return a graceful error.
        return jsonify({
            'success': False,
            'error': 'Basic Pitch is not installed. Run: pip install basic-pitch'
        }), 500

    try:
        # bp_predict() is the core Basic Pitch function (imported above as alias).
        # It reads the audio file and returns three objects:
        #
        #   model_output  — raw neural network arrays (we don't use these)
        #   midi_data     — a MIDI representation (like digital sheet music)
        #   note_events   — a list of detected notes with timing
        #
        # Each item in note_events is a tuple:
        #   (start_seconds, end_seconds, midi_pitch, amplitude, pitch_bends)

        model_output, midi_data, note_events = bp_predict(
            save_path,
            ICASSP_2022_MODEL_PATH
        )

        # ── Build a clean list of notes for the frontend ──────────────────

        notes_list = []
        for note in note_events:
            start    = float(note[0])
            end      = float(note[1])
            pitch    = int(note[2])
            conf     = float(note[3])   # 0.0–1.0

            notes_list.append({
                'note':        midi_to_note_name(pitch),
                'start':       round(start, 2),
                'end':         round(end, 2),
                'duration':    round(end - start, 2),
                'confidence':  round(conf * 100),   # convert to percentage integer
                'string_area': guitar_string_area(pitch)
            })

        # ── Build summary statistics ──────────────────────────────────────

        total = len(notes_list)

        if total == 0:
            os.remove(save_path)
            return jsonify({
                'success': False,
                'error': 'No notes detected. Try a clearer recording with less background noise, or make sure your guitar is audible in the recording.',
            })

        unique_notes    = sorted(set(n['note'] for n in notes_list))
        avg_confidence  = round(sum(n['confidence'] for n in notes_list) / total)
        recording_length = round(float(note_events[-1][1]), 1)
        # note_events[-1] is the last detected note; [1] is its end time in seconds.

        notes_per_second = round(total / recording_length, 1) if recording_length > 0 else 0

        # Interpret the confidence score in plain English
        if avg_confidence >= 70:
            confidence_label = 'High — notes were clear and well-defined'
        elif avg_confidence >= 40:
            confidence_label = 'Medium — some notes were unclear (try reducing background noise)'
        else:
            confidence_label = 'Low — recording may have too much noise or the instrument was quiet'

        summary = {
            'total_notes':        total,
            'unique_notes':       unique_notes,
            'avg_confidence':     avg_confidence,
            'confidence_label':   confidence_label,
            'recording_length':   recording_length,
            'notes_per_second':   notes_per_second
        }

        os.remove(save_path)
        return jsonify({
            'success':  True,
            'filename': safe_name,
            'message':  f'Analysis complete — {total} notes detected across {recording_length}s.',
            'notes':    notes_list,
            'summary':  summary
        })

    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({
            'success': False,
            'error':   'Analysis failed — the file may be corrupted or in an unsupported format. Try converting to MP3 or WAV and uploading again.',
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
