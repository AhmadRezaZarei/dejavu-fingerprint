from flask import Flask, jsonify
import argparse
import json
import sys
from argparse import RawTextHelpFormatter
from os.path import isdir
from flask import request
from werkzeug.utils import secure_filename
import os
import time
from dejavu import Dejavu
from pydub import AudioSegment
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
# from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer
from dotenv import load_dotenv
from acrcloud import AcrCloud

DEFAULT_CONFIG_FILE = "dejavu.cnf.SAMPLE"

app = Flask(__name__)

def convert_mp3_to_ogg(filePath, export_dir):
    resultName = export_dir + "/ exported_ogg_" + str(time.time()) + ".ogg"
    AudioSegment.from_mp3(filePath).export(resultName, format="ogg")
    return resultName

def trim_mp3(filepath, export_dir, start, end):
    song = AudioSegment.from_mp3(filepath)
    exp = song[start : end]
    resultName = export_dir + "/exported_trim_" + str(time.time()) + ".mp3"
    exp.export(resultName, format="mp3")
    return resultName


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
    return {"error": None}


@app.route("/set-song-meta", methods=['POST'])
def set_song_meta():
    song_id = request.json["song_id"]
    song_meta = request.json["song_meta"]
    dejavu.update_song_meta(song_id, song_meta)
    return jsonify({"error": None})

@app.route("/meta-less-songs", methods=['GET'])
def get_meta_less_songs():
    return  jsonify({"songs": dejavu.fetch_meta_less_songs()})

@app.route("/recognize", methods=['POST'])
def recognize():

    if 'file' not in request.files.keys():
        print("file is not on the request")
        return {"error": {"type": 400, "message": "can not found file"}}, 400
    
    f = request.files['file']
    filepath = "./songs/" + secure_filename(f.filename)
    f.save(filepath)
    songs = dejavu.recognize(FileRecognizer, filepath)
    convert_bytes_to_string(songs)
    os.remove(filepath)

    foundSongs = songs["results"]
    matched_index = 0
    matched_confidence = 0.0
    for idx, fSong in enumerate(foundSongs):
        if idx == 0:
            matched_confidence = float(fSong["input_confidence"])
            matched_index = 0
            continue
        cur_confidence = float(fSong["input_confidence"])
        if cur_confidence > matched_confidence:
            matched_index = idx
            matched_confidence = cur_confidence
    
    if matched_confidence > 0.2:
        return {"matched_song": foundSongs[matched_index] }, 200
    
    trim_mp3_path = trim_mp3(filepath, "songs", 0, 9500)

    cnv_ogg = convert_mp3_to_ogg(trim_mp3_path, "songs")

    os.remove(trim_mp3_path)

    statusCode, jsonResult = acrCloud.recognize(cnv_ogg)
    return jsonResult, statusCode


if __name__ == '__main__':
    
    load_dotenv()

    def_conf_path = DEFAULT_CONFIG_FILE
    
    env_conf_path = os.getenv('MYSQL_DB_CONFIG_PATH')
    if env_conf_path != None:
        def_conf_path = env_conf_path

    print("config path: " + def_conf_path)

    dejavu = init(def_conf_path)

    access_key = accessKey = "ddedafe38ced443465d976877e1598c8"
    access_secret = "qgFa6rdTmFkIZkHsD2ymDXvXiOT4yqxneRjeqKcM"
    req_url = "https://identify-eu-west-1.acrcloud.com/v1/identify"

    acrCloud = AcrCloud(access_key, access_secret, req_url)
    
    app.run(host="0.0.0.0", port="5678",debug=True)