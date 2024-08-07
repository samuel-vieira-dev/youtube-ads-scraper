import yt_dlp as youtube_dl
import imageio_ffmpeg
import requests
import os

def download_and_transcribe_audio(url):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + '.mp3'
    
    transcription = ""
    api_key = os.getenv("OPENAI_API_KEY")
    try:
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        data = {
            'model': 'whisper-1',
            'response_format': 'text'
        }
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            response = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, files=files, data=data)
            transcription = response.text
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
    
    return transcription
