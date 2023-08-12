from flask import Flask
from flask import request
from werkzeug.utils import secure_filename

app = Flask(__name__)

# initialize dejavu 



@app.route("/fingerprint", methods= ['POST'])
def fingerprint_file():
    f = request.files['file']
    f.save("./songs/" + secure_filename(f.filename))
    song_name = request.form['song_name']
    return song_name

@app.route("/recognize", methods= ['POST'])
def recognize():
    return "ping"