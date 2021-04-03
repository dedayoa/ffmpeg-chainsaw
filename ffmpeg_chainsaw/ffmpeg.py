import logging
import os
import subprocess
import tempfile

from .exceptions import DecodeError
from .uploader import UploadTransmitter

logger = logging.getLogger(__name__)

def process_file(file_loc, ffmpeg_args, upload_transmitter: UploadTransmitter):
    
    output_file = os.path.join(tempfile.gettempdir(), upload_transmitter.file_name)
    output = open(output_file, "wb")
    
    conversion_command = [
        "ffmpeg",
        "-i", file_loc,
        *ffmpeg_args,
        output.name
    ]
    
    p = subprocess.Popen(conversion_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p_out, p_err = p.communicate()
    
    if p.returncode != 0:
        raise DecodeError(f"Decoding failed. ffmpeg returned error code: {p.returncode}\n\nOutput from ffmpeg/avlib:\n\n{p_err}\n\n{p_out}")
    
    output.close()
    print("process complete")

    os.remove(file_loc)
    upload_transmitter(output)

