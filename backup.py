from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import yt_dlp as youtube_dl
import imageio_ffmpeg
import requests
import json
import re
import time
import os

# Configuração e inicialização do driver
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--log-level=3')
    options.add_argument('--silent') 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    return driver

# Função para determinar se o vídeo é um short
def is_youtube_short(video_url):
    return '/shorts/' in video_url

# Função para extrair dados do vídeo
def get_video_data(driver, video_url):
    driver.get(video_url)
    time.sleep(5)
    
    video_data = {}
    try:
        video_title = driver.find_element(By.XPATH, '//*[@id="title"]/h1/yt-formatted-string').text
        channel_name = driver.find_element(By.XPATH, '//*[@id="text"]/a').text
        views = driver.find_element(By.XPATH, '//*[@id="info"]/span[1]').text
        likes = driver.find_element(By.XPATH, '//*[@id="top-level-buttons-computed"]/segmented-like-dislike-button-view-model/yt-smartimation/div/div/like-button-view-model/toggle-button-view-model/button-view-model/button/div[2]').text
        date_published = driver.find_element(By.XPATH, '//*[@id="info"]/span[3]').text
        video_duration = driver.find_element(By.CSS_SELECTOR, 'span.ytp-time-duration').text
        is_short = is_youtube_short(video_url)
        
        # Adiciona transcrição ao vídeo
        transcription = download_and_transcribe_audio(video_url)

        video_data = {
            "video_title": video_title,
            "channel_name": channel_name,
            "views": views,
            "date_published": date_published,
            "likes": likes,
            "video_duration": video_duration,
            "is_short": is_short,
            "transcription": transcription,
        }
    except Exception as e:
        print(f"Erro ao extrair dados do vídeo: {str(e)}")
    
    return video_data

# Função para expandir anúncios de vídeo
def expand_video_ads(driver, max_videos):
    try:
        todos_os_formatos = driver.find_element(By.XPATH, "//div[contains(text(), 'Todos os formatos')]")
        todos_os_formatos.click()
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao clicar em 'Todos os Formatos': {str(e)}")

    try:
        video_option = driver.find_element(By.XPATH, "//div[contains(text(), 'Vídeo')]")
        video_option.click()
        time.sleep(5)
    except Exception as e:
        print(f"Erro ao selecionar a opção 'Vídeo': {str(e)}")

    try:
        see_all_ads_button = driver.find_element(By.CSS_SELECTOR, ".grid-expansion-button")
        see_all_ads_button.click()
        time.sleep(5) 
    except Exception as e:
        print(f"Erro ao clicar no botão 'See all ads': {str(e)}")

    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        ad_elements = driver.find_elements(By.CSS_SELECTOR, 'creative-preview')
        num_videos = len(ad_elements)
        if new_height == last_height or num_videos >= max_videos:
            break
        
        last_height = new_height

# Função para extrair anúncios do YouTube
def get_youtube_ads(domain, max_videos):
    driver = setup_driver()
    url = f"https://adstransparency.google.com/?hl=pt-BR&region=anywhere&platform=YOUTUBE&domain={domain}"
    driver.get(url)
    time.sleep(5)

    expand_video_ads(driver, max_videos)

    ads = []
    ad_elements = driver.find_elements(By.CSS_SELECTOR, 'creative-preview')
    
    for i, ad in enumerate(ad_elements):
        if i >= max_videos:
            break

        try:
            thumbnail_url = ad.find_element(By.TAG_NAME, 'img').get_attribute('src')
            video_id_match = re.search(r'/vi/(.*?)/hqdefault.jpg', thumbnail_url)
            if video_id_match:
                video_id = video_id_match.group(1)
                video_url = f'https://www.youtube.com/watch?v={video_id}'

                ads.append({
                    'thumbnail_link': thumbnail_url,
                    'video_link': video_url
                })
        except Exception as e:
            print(f"Erro ao extrair dados do anúncio: {str(e)}")

    driver.quit()
    return ads

# Função para salvar dados em JSON
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Função para carregar dados existentes
def load_existing_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Função para baixar e transcrever áudio
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
    try:
        headers = {
            'Authorization': 'Bearer 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'
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

# Função principal
def main():
    domains = input("Insira um ou mais domínios ou landing pages (separados por vírgula): ").split(',')
    max_videos = int(input("Quantos vídeos no máximo você deseja buscar? "))
    existing_data = load_existing_data('data/youtube_ads.json')
    
    for domain in domains:
        domain = domain.strip()
        if domain not in existing_data:
            existing_data[domain] = []

        ads = get_youtube_ads(domain, max_videos)
        
        driver = setup_driver()
        for ad in ads:
            if ad['video_link'] not in [video['video_link'] for video in existing_data[domain]]:
                video_data = get_video_data(driver, ad['video_link'])
                ad.update(video_data)
                existing_data[domain].append(ad)

        driver.quit()

    save_to_json(existing_data, 'data/youtube_ads.json')
    print("Dados dos anúncios atualizados salvos em 'data/youtube_ads.json'")

if __name__ == '__main__':
    main()
