from flask import Flask, jsonify
import argparse
import json
import sys
from argparse import RawTextHelpFormatter
from os.path import isdir
from flask import request
from werkzeug.utils import secure_filename
import os
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer
from dotenv import load_dotenv

DEFAULT_CONFIG_FILE = "dejavu.cnf.SAMPLE"

app = Flask(__name__)

def convert_bytes_to_string(songs):
    for key, value in songs.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    convert_bytes_to_string(item)
        elif isinstance(value, bytes):
            songs[key] = str(value, "utf-8")
        elif isinstance(value, dict):
            convert_bytes_to_string(value)
        else:
            songs[key] = str(value)

def init(configpath):
    """
    Load config from a JSON file
    """
    try:
        with open(configpath) as f:
            config = json.load(f)
    except IOError as err:
        print(f"Cannot open configuration: {str(err)}. Exiting")
        sys.exit(1)

    # create a Dejavu instance
    return Dejavu(config)


@app.route("/fingerprint", methods= ['POST'])
def fingerprint_file():
    f = request.files['file']
    filepath = "./songs/" + secure_filename(f.filename)
    f.save(filepath)
    song_name = request.form['song_name']
    dejavu.fingerprint_file(filepath)
    os.remove(filepath)
    return song_name

@app.route("/recognize", methods=['POST'])
def recognize():
    f = request.files['file']
    filepath = "./songs/" + secure_filename(f.filename)
    f.save(filepath)
    songs = dejavu.recognize(FileRecognizer, filepath)
    convert_bytes_to_string(songs)
    os.remove(filepath)
    return json.dumps(songs, indent=4)


if __name__ == '__main__':
    
    load_dotenv()

    def_conf_path = DEFAULT_CONFIG_FILE
    
    env_conf_path = os.getenv('MYSQL_DB_CONFIG_PATH')
    if env_conf_path != None:
        def_conf_path = env_conf_path

    print("config path: " + def_conf_path)
    
#    try :
    dejavu = init(def_conf_path)
#    print("dejavu created")
#    except Exception as err:
#        print("exception !!!!! ", err)
    
    app.run(host="0.0.0.0", port="5678",debug=True)
    pass