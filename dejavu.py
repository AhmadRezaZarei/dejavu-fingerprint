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

    print("config path: " + def_conf_path + "\n")
    
    try :
        dejavu = init(def_conf_path)
        print("dejavu created")
    except Exception as err:
        print("exception !!!!! ", err)
    
    app.run(host="0.0.0.0", port="5678",debug=True)
    pass

# if __name__ == '__main__w':
#     parser = argparse.ArgumentParser(
#         description="Dejavu: Audio Fingerprinting library",
#         formatter_class=RawTextHelpFormatter)
#     parser.add_argument('-c', '--config', nargs='?',
#                         help='Path to configuration file\n'
#                              'Usages: \n'
#                              '--config /path/to/config-file\n')
#     parser.add_argument('-f', '--fingerprint', nargs='*',
#                         help='Fingerprint files in a directory\n'
#                              'Usages: \n'
#                              '--fingerprint /path/to/directory extension\n'
#                              '--fingerprint /path/to/directory')
#     parser.add_argument('-r', '--recognize', nargs=2,
#                         help='Recognize what is '
#                              'playing through the microphone or in a file.\n'
#                              'Usage: \n'
#                              '--recognize mic number_of_seconds \n'
#                              '--recognize file path/to/file \n')
#     args = parser.parse_args()

#     if not args.fingerprint and not args.recognize:
#         parser.print_help()
#         sys.exit(0)

#     config_file = args.config
#     if config_file is None:
#         config_file = DEFAULT_CONFIG_FILE

#     djv = init(config_file)
#     if args.fingerprint:
#         # Fingerprint all files in a directory
#         if len(args.fingerprint) == 2:
#             directory = args.fingerprint[0]
#             extension = args.fingerprint[1]
#             print(f"Fingerprinting all .{extension} files in the {directory} directory")
#             djv.fingerprint_directory(directory, ["." + extension], 4)

#         elif len(args.fingerprint) == 1:
#             filepath = args.fingerprint[0]
#             if isdir(filepath):
#                 print("Please specify an extension if you'd like to fingerprint a directory!")
#                 sys.exit(1)
#             djv.fingerprint_file(filepath)

#     elif args.recognize:
#         # Recognize audio source
#         songs = None
#         source = args.recognize[0]
#         opt_arg = args.recognize[1]

#         if source in ('mic', 'microphone'):
#             songs = djv.recognize(MicrophoneRecognizer, seconds=opt_arg)
#         elif source == 'file':
#             songs = djv.recognize(FileRecognizer, opt_arg)
#         print(songs)
