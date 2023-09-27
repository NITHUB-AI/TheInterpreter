import time
import uuid

# prefer os.mktemp() where possible?
def generate_filename(prefix='tmp_', extension=''):
    if not extension:
        raise ValueError("extension must be specified")

    random_string = str(uuid.uuid4().hex[:6])
    current_time = int(time.time())
    filename = f'{prefix}{current_time}_{random_string}{extension}'
    return filename

def get_audio_bytes(file: str):
    with open(file, 'rb') as audio:
        return audio.read()