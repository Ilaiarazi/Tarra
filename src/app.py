import json
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(override=True)

import anthropic
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, abort,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from . import db

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

# The secret key signs the session cookie so users can't tamper with their
# login state. For local dev a fixed fallback is fine; set FLASK_SECRET_KEY in
# .env (any long random string) before deploying anywhere real.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-change-me')

# Create the users/analyses tables on startup if they don't exist yet.
db.init_db()

# ── Upload settings ───────────────────────────────────────────────────────────
UPLOAD_FOLDER     = 'uploads'
# Audio we can hand straight to Basic Pitch.
AUDIO_EXTENSIONS  = {'mp3', 'wav'}
# Video / compressed-audio containers we extract the audio out of first.
# Covers what an iPhone produces: camera clips (.mov/.mp4) and Voice Memos (.m4a).
VIDEO_EXTENSIONS  = {'mov', 'mp4', 'm4v', 'm4a', 'aac', 'webm', '3gp'}
ALLOWED_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS
# Videos are far bigger than audio, so the ceiling is generous. A short phone
# clip is usually well under this.
MAX_FILE_SIZE     = 200 * 1024 * 1024   # 200 MB in bytes

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


@app.errorhandler(413)
def file_too_large(_e):
    """Flask rejects over-limit uploads before our route runs — answer in JSON."""
    limit_mb = MAX_FILE_SIZE // (1024 * 1024)
    return jsonify({
        'success': False,
        'error': f'That file is over the {limit_mb} MB limit. Try a shorter clip.',
    }), 413


# ── Login state ───────────────────────────────────────────────────────────────
# We keep the logged-in user's id and name in Flask's session (a signed cookie).
# current_user() reads it back; the context processor makes `user` available in
# every template automatically, so the nav can show the right links everywhere.

def current_user():
    """Return {'id', 'username'} for the logged-in user, or None if logged out."""
    if 'user_id' in session:
        return {'id': session['user_id'], 'username': session['username']}
    return None


@app.context_processor
def inject_user():
    return {'user': current_user()}


def _friendly_date(iso_string):
    """Turn a stored ISO timestamp into something like '16 Jun 2026, 14:03'."""
    try:
        return datetime.fromisoformat(iso_string).strftime('%-d %b %Y, %H:%M')
    except (ValueError, TypeError):
        return iso_string


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
    """True for supported audio (mp3/wav) and video (mov/mp4/…) files."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_ext(filename):
    """Lowercase extension without the dot, e.g. 'clip.MOV' → 'mov'."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


# ── Helper: pull audio out of a video ─────────────────────────────────────────
# iPhone recordings arrive as .mov/.mp4 with the audio as a track inside the
# video container. Basic Pitch only reads audio, so we extract the audio track
# to a temporary WAV first. imageio-ffmpeg ships a static ffmpeg binary, so this
# works even without a system ffmpeg install.

def _ffmpeg_path():
    """Locate an ffmpeg binary — a system one if present, else the bundled one."""
    from shutil import which
    system = which('ffmpeg')
    if system:
        return system
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def extract_audio(video_path):
    """
    Extract the audio track of a video into a mono 22.05 kHz WAV and return its
    path. Raises RuntimeError with a user-facing message if it can't.
    """
    ffmpeg = _ffmpeg_path()
    if not ffmpeg:
        raise RuntimeError('Video support needs ffmpeg. Run: pip install imageio-ffmpeg')

    wav_path = video_path + '.extracted.wav'
    result = subprocess.run(
        [ffmpeg, '-y', '-i', video_path,
         '-vn',            # drop the video stream — we only want the audio
         '-ac', '1',       # mix down to mono
         '-ar', '22050',   # 22.05 kHz (Basic Pitch resamples to this anyway)
         '-f', 'wav', wav_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
        # The usual real cause is a clip with no audio track (or a muted one).
        raise RuntimeError("Couldn't find any audio in that video. Make sure the clip isn't muted.")
    return wav_path


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


# ── Auth ────────────────────────────────────────────────────────────────────────

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Create a new account. GET shows the form; POST processes it."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Basic validation with friendly, specific messages.
        if not username or not password:
            return render_template('signup.html', error='Please fill in both fields.', username=username)
        if len(username) < 3:
            return render_template('signup.html', error='Username must be at least 3 characters.', username=username)
        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters.', username=username)
        if db.get_user_by_username(username):
            return render_template('signup.html', error='That username is already taken.', username=username)

        # Store only the hash, never the raw password.
        user_id = db.create_user(username, generate_password_hash(password))
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log into an existing account."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = db.get_user_by_username(username)
        # Same message whether the username or the password is wrong — don't
        # reveal which usernames exist.
        if user is None or not check_password_hash(user['password_hash'], password):
            return render_template('login.html', error='Wrong username or password.', username=username)

        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear the session and return to the landing page."""
    session.clear()
    return redirect(url_for('home'))


@app.route('/history')
def history():
    """List the logged-in user's saved analyses, newest first."""
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    analyses = []
    for row in db.list_analyses(user['id']):
        analyses.append({
            'id':         row['id'],
            'filename':   row['filename'],
            'created_at': _friendly_date(row['created_at']),
            'summary':    json.loads(row['summary_json']),
        })
    return render_template('history.html', analyses=analyses)


@app.route('/analysis/<int:analysis_id>')
def view_analysis(analysis_id):
    """Render the dashboard for one saved analysis, scoped to its owner."""
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    row = db.get_analysis(analysis_id, user['id'])
    if row is None:
        abort(404)

    saved_data = {
        'filename': row['filename'],
        'summary':  json.loads(row['summary_json']),
        'notes':    json.loads(row['notes_json']),
    }
    return render_template('results.html', saved_data=saved_data)


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
    Receives an audio or video file, saves it, extracts the audio track if it's
    a video, runs Basic Pitch, and returns the detected notes as JSON.
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
                        'error': 'Please upload an audio file (MP3 or WAV) or a video (MOV or MP4).'}), 400

    if not BASIC_PITCH_READY:
        # basic-pitch wasn't importable at startup — return a graceful error.
        return jsonify({
            'success': False,
            'error': 'Basic Pitch is not installed. Run: pip install basic-pitch'
        }), 500

    # ── Save the upload to disk ───────────────────────────────────────────────
    # secure_filename strips dangerous characters like '..' or '/' so the file
    # can't escape the uploads folder.
    safe_name = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    file.save(save_path)

    extracted_path = None   # set when we pull audio out of a video

    try:
        # A video (or compressed-audio container) needs its audio pulled out to
        # a WAV before Basic Pitch can read it. Plain MP3/WAV go straight in.
        if file_ext(safe_name) in VIDEO_EXTENSIONS:
            extracted_path = extract_audio(save_path)
            audio_path = extracted_path
        else:
            audio_path = save_path

        # bp_predict() returns (model_output, midi_data, note_events); each note
        # event is a tuple: (start_s, end_s, midi_pitch, amplitude, pitch_bends).
        model_output, midi_data, note_events = bp_predict(audio_path, ICASSP_2022_MODEL_PATH)

        # ── Build a clean list of notes for the frontend ──────────────────
        notes_list = []
        for note in note_events:
            start = float(note[0])
            end   = float(note[1])
            pitch = int(note[2])
            conf  = float(note[3])   # 0.0–1.0
            notes_list.append({
                'note':        midi_to_note_name(pitch),
                'start':       round(start, 2),
                'end':         round(end, 2),
                'duration':    round(end - start, 2),
                'confidence':  round(conf * 100),   # convert to percentage integer
                'string_area': guitar_string_area(pitch),
            })

        total = len(notes_list)
        if total == 0:
            return jsonify({
                'success': False,
                'error': 'No notes detected. Try a clip where the guitar is loud and up front, with less background noise.',
            })

        # ── Build summary statistics ──────────────────────────────────────
        unique_notes     = sorted(set(n['note'] for n in notes_list))
        avg_confidence   = round(sum(n['confidence'] for n in notes_list) / total)
        recording_length = round(float(note_events[-1][1]), 1)
        notes_per_second = round(total / recording_length, 1) if recording_length > 0 else 0

        if avg_confidence >= 70:
            confidence_label = 'High — notes were clear and well-defined'
        elif avg_confidence >= 40:
            confidence_label = 'Medium — some notes were unclear (try reducing background noise)'
        else:
            confidence_label = 'Low — recording may have too much noise or the instrument was quiet'

        summary = {
            'total_notes':      total,
            'unique_notes':     unique_notes,
            'avg_confidence':   avg_confidence,
            'confidence_label': confidence_label,
            'recording_length': recording_length,
            'notes_per_second': notes_per_second,
        }

        # If the user is logged in, save this analysis to their history so they
        # can revisit it later. Logged-out users still get results — just not saved.
        saved_id = None
        user = current_user()
        if user:
            saved_id = db.save_analysis(user['id'], safe_name, summary, notes_list)

        return jsonify({
            'success':  True,
            'filename': safe_name,
            'message':  f'Analysis complete — {total} notes detected across {recording_length}s.',
            'notes':    notes_list,
            'summary':  summary,
            'saved_id': saved_id,
        })

    except RuntimeError as e:
        # Friendly errors we raised ourselves (e.g. a video with no audio track).
        return jsonify({'success': False, 'error': str(e)}), 400

    except Exception:
        return jsonify({
            'success': False,
            'error':   'Analysis failed — the file may be corrupted or in an unsupported format. Try a different clip, or convert it to MP3 or WAV.',
        }), 500

    finally:
        # Always clean up the uploaded file and any audio we extracted from it.
        for path in (save_path, extracted_path):
            if path and os.path.exists(path):
                os.remove(path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
