from scraper import get_youtube_ads, setup_driver, get_video_data
from utils import save_to_json, load_existing_data

def main():
    domains = input("Insira um ou mais domínios ou landing pages (separados por vírgula): ").split(',')
    max_videos_input = input("Quantos vídeos no máximo você deseja buscar? (Padrão é 3, máximo é 10): ")

    try:
        max_videos = int(max_videos_input)
        if max_videos > 10:
            max_videos = 10
        elif max_videos < 1:
            max_videos = 3
    except ValueError:
        max_videos = 3

    existing_data = load_existing_data('data/youtube_ads.json')

    for domain in domains:
        domain = clean_url(domain.strip())
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

def clean_url(url):
    return url.replace("https://", "").replace("http://", "").replace("www.", "")

if __name__ == '__main__':
    main()
