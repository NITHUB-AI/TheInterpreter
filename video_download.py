import subprocess
import tempfile

def download_youtube_video(youtube_url, filename):
     # "youtube_video" #subprocess.getoutput(f'yt-dlp --print filename {youtube_url}')
    result = subprocess.call(f"yt-dlp -o {filename} {youtube_url} -S res,ext:mp4:m4a --recode mp4", shell=True)
    if not result:
        print(f"Video downloaded.")
        return filename
    else:
        print("Something went wrong...")
        return False

if __name__ == '__main__':
    file = download_youtube_video("https://www.youtube.com/watch?v=dATbIVM_248")
