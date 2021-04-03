import subprocess
from tempfile import NamedTemporaryFile
import logging
from .exceptions import DecodeError
from .uploader import UploadTransmitter
import os


logger = logging.getLogger(__name__)

def process_file(file_loc, ffmpeg_args, upload_transmitter: UploadTransmitter):
     
    output = NamedTemporaryFile(mode="rb", delete=True)
    #conversion_command = "ffmpeg -i %s -acodec pcm_s16le -ac 1 -f wav -vn -y -ar 8000 %s"%(input.name, output.name)
    
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
    
    output.seek(0)
    print("process complete")
    
    os.remove(file_loc)
    upload_transmitter(output)

