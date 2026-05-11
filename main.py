import os                                  # os lets us create folders and build file paths
from flask import Flask, render_template, request, jsonify
# render_template → serves our HTML page
# request         → gives us access to data sent by the browser (files, form fields, etc.)
# jsonify         → converts a Python dict into a proper JSON response

from werkzeug.utils import secure_filename
# secure_filename() cleans up filenames to prevent security attacks.
# e.g. if someone uploads a file called "../../etc/passwd", secure_filename
# strips the dangerous path and returns just "etc_passwd" (harmless).

app = Flask(__name__)

# ── Upload configuration ──────────────────────────────────────────────────────

# Where uploaded files will be stored. 'uploads' means a folder called
# 'uploads' inside the same directory as main.py.
UPLOAD_FOLDER = 'uploads'

# A Python set (like a list but faster to look up) of allowed file extensions.
# Only MP3 and WAV are accepted.
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

# 10 MB in bytes. Python evaluates 10 * 1024 * 1024 = 10,485,760 bytes.
MAX_FILE_SIZE = 10 * 1024 * 1024

# os.makedirs creates the 'uploads' folder if it doesn't already exist.
# exist_ok=True means "don't crash if the folder is already there".
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store these settings in Flask's config dictionary so any part of the
# app can read them with app.config['KEY'].
app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
# MAX_CONTENT_LENGTH is a special Flask setting — Flask will automatically
# reject any request whose body is larger than this value (returns 413 error).


# ── Helper function ───────────────────────────────────────────────────────────

def allowed_file(filename):
    """
    Returns True if the filename ends in .mp3 or .wav (case-insensitive).

    How it works:
      'my_song.MP3'.rsplit('.', 1)  →  ['my_song', 'MP3']
      [1]                           →  'MP3'
      .lower()                      →  'mp3'
      in ALLOWED_EXTENSIONS         →  True  ✓

    The 'in filename' check first makes sure there IS a dot —
    a file called just 'mysong' (no extension) would return False.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    # Serve the animated landing page from templates/index.html
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles audio file uploads from the frontend.

    methods=['POST'] means this route ONLY responds to POST requests.
    A POST request is used when the browser is sending data to the server
    (as opposed to GET, which just fetches a page).
    """

    # request.files is a dictionary of all files sent with the request.
    # We check if the key 'file' exists — this matches formData.append('file', ...)
    # in the JavaScript. If the key is missing, something went wrong on the frontend.
    if 'file' not in request.files:
        # jsonify() turns a Python dict into a JSON string response.
        # 400 is the HTTP status code for "Bad Request".
        return jsonify({'success': False, 'error': 'No file was sent.'}), 400

    # Get the actual file object from the request.
    file = request.files['file']

    # If the user submitted the form without choosing a file,
    # the filename will be an empty string.
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected.'}), 400

    # Run the filename through our allowed_file() helper.
    if not allowed_file(file.filename):
        return jsonify({'success': False,
                        'error': 'Only MP3 and WAV files are allowed.'}), 400

    # secure_filename() sanitises the filename — removes slashes, dots that
    # could navigate up directories, spaces, etc.
    # Example: '../../../evil.mp3' → 'evil.mp3'
    safe_name = secure_filename(file.filename)

    # Build the full path where the file will be saved on disk.
    # os.path.join() combines paths correctly on any OS:
    #   os.path.join('uploads', 'my_song.mp3')  →  'uploads/my_song.mp3'
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)

    # Actually write the file to disk at the path we just built.
    file.save(save_path)

    # Return a JSON success response. The frontend's fetch() call will receive
    # this and use data.message to update the page.
    return jsonify({
        'success':  True,
        'filename': safe_name,
        'message':  f'File received! \u201c{safe_name}\u201d is ready for analysis.'
    })


# ── Dev server entry point ────────────────────────────────────────────────────

if __name__ == '__main__':
    # This block only runs when you execute 'python3 main.py' directly.
    # When Replit uses gunicorn (the production server), it imports the 'app'
    # object instead — so this block is skipped in production.
    app.run(host='0.0.0.0', port=8080)
