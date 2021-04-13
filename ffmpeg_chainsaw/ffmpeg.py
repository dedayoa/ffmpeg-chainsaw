import logging
import os
import subprocess
import tempfile

from .helpers import thread_it, send_update
from .uploader import UploadTransmitter

logger = logging.getLogger(__name__)


# TODO: filter flags/commands passed to ffmpeg. See https://gist.github.com/tayvano/6e2d456a9897f55025e25035478a3a50
@thread_it
def process_file(file_loc, ffmpeg_args, upload_transmitter: UploadTransmitter,
                 update_callback_data) -> None:
    """Runs the ffmpeg command as a subprocess and calls function to upload the processed file.

    Args:
        file_loc (Path): the location of the source file
        ffmpeg_args (list): the ffmpeg flags/commands
        upload_transmitter (UploadTransmitter): object that uploads the processed file
        update_callback_data (function): data to configure function to send update data.

    Returns:
        
    """

    output_file = os.path.join(tempfile.gettempdir(),
                               upload_transmitter.file_name)
    output = open(output_file, "wb")

    conversion_command = [
        "ffmpeg", "-i",
        str(file_loc), *ffmpeg_args, output.name
    ]

    p = subprocess.Popen(conversion_command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p_out, p_err = p.communicate()

    output.close()
    os.remove(file_loc)

    if p.returncode != 0:
        msg = f"Decoding failed. ffmpeg returned error code: {p.returncode}\n\nOutput from ffmpeg/avlib:\n\n{p_err}\n\n{p_out}"
        logger.error(msg)
        send_update('ERROR', msg, update_callback_data)
    else:
        msg = f'FFMpeg process "{" ".join(conversion_command)}" completed successfully'
        logger.info(msg)
        send_update('INFO', msg, update_callback_data)

        upload_transmitter(output, update_callback_data)