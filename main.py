from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Tarra is live</h1><p>Your guitar app is on its way.</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)