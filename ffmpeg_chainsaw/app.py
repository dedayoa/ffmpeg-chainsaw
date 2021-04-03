import json
import mimetypes
import uuid
import threading
import psutil

from flask import Blueprint, current_app, jsonify, request
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .exceptions import HTTPException
from .ffmpeg import process_file
from .schema import instruction_schema
from .uploader import UploadTransmitter

bp = Blueprint('app', __name__, url_prefix='')


@bp.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@bp.route('/')
def hello():
    return 'Hello World'


@bp.route('/upload_process/', methods=['POST'])
def upload_to_process():
    """
    Uploads file to begin processing
    """
    if 'file' not in request.files:
        raise HTTPException('file is missing')
    f = request.files['file']

    file_name = str(uuid.uuid4())
    file_loc = current_app.config.get('BASE_DIR').joinpath(
        'incoming', file_name)
    f.save(file_loc)

    data = request.form.to_dict()
    instruction = json.loads(data.get('instruction'))

    try:
        validate(instruction, instruction_schema)
    except ValidationError as e:
        raise HTTPException(f'invalid instruction: {e.message}')

    ffmeg_arguments = instruction.get('ffmpegArgs')
    output_file_ext = instruction.get('outputFileExt')
    output_file_name = f"{instruction.get('outputFileName', file_name)}.{output_file_ext}"
    
    guessed_mime_type = mimetypes.guess_type(output_file_name)[0]
    output_file_mimetype = instruction.get('outputFileMimeType',
                                           guessed_mime_type)
    destination = instruction.get('destination', None)

    upload_transmitter = UploadTransmitter(output_file_name, output_file_mimetype, destination)

    # process file in background
    if psutil.cpu_percent(interval=1) > 95:
        raise HTTPException("server CPU at full load", 503)
    
    thread = threading.Thread(target=process_file, args=(
        file_loc, ffmeg_arguments, upload_transmitter
    ))
    thread.daemon = True
    thread.start()

    return {"message": instruction}


@bp.route('/get_process/', methods=['POST'])
def get_to_process():
    """
    Will download the file to begin processing 
    """
    pass
