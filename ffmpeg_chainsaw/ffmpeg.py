import logging
import os
import subprocess
import tempfile

from .exceptions import DecodeError
from .helpers import thread_it, send_update
from .uploader import UploadTransmitter

logger = logging.getLogger(__name__)

#TODO filter flags/commands passed to ffmpeg. See https://gist.github.com/tayvano/6e2d456a9897f55025e25035478a3a50
@thread_it
def process_file(file_loc, ffmpeg_args, upload_transmitter: UploadTransmitter, update_callback_data):
    
    output_file = os.path.join(tempfile.gettempdir(), upload_transmitter.file_name)
    output = open(output_file, "wb")
    
    conversion_command = [
        "ffmpeg",
        "-i", str(file_loc),
        *ffmpeg_args,
        output.name
    ]
    
    p = subprocess.Popen(conversion_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p_out, p_err = p.communicate()
    
    error_occured = False
    
    if p.returncode != 0:
        error_occured = True
        msg = f"Decoding failed. ffmpeg returned error code: {p.returncode}\n\nOutput from ffmpeg/avlib:\n\n{p_err}\n\n{p_out}"
        logger.error(msg)
        send_update(
            'ERROR', msg,
            update_callback_data)
    output.close()
    os.remove(file_loc)
    
    if not error_occured:
        msg = f'FFMpeg process "{" ".join(conversion_command)}" completed successfully'
        logger.info(msg)
        send_update(
                'INFO', msg,
                update_callback_data)

        upload_transmitter(output, update_callback_data)