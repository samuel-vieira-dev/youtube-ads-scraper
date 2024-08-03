from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
from transcriber import download_and_transcribe_audio  # Certifique-se de importar a função aqui

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

def is_youtube_short(video_url):
    return '/shorts/' in video_url

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
