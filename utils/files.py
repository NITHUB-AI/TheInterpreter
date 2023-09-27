import time
import uuid

def generate_filename(prefix='', extension=''):
    random_string = str(uuid.uuid4().hex[:6])
    current_time = int(time.time())
    filename = f'{prefix}{current_time}_{random_string}{extension}'
    return filename