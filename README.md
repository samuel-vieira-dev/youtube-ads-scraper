# YouTube Ads Scraper

Este projeto é um scraper de anúncios do YouTube que coleta dados de anúncios de vídeo para um ou mais domínios ou landing pages usando a biblioteca de transparência de anúncios do Google.

## Funcionalidades

- **Coleta de Dados de Anúncios**: Extrai informações sobre anúncios de vídeo, incluindo título do vídeo, título do canal, duração do vídeo, quantidade de visualizações, quantidade de likes, link da thumbnail, se é um YouTube Short, transcrição do vídeo e data de publicação.

- **Suporte a Múltiplos Domínios**: Permite a inserção de um ou mais domínios ou landing pages para coletar dados de anúncios.

- **Paralelização**: Utiliza execução paralela para acelerar a coleta de dados e processamento de transcrições.

- **Transcrição de Áudio**: Baixa o áudio do vídeo e utiliza a API da OpenAI para transcrever o conteúdo.

## Requisitos

- Python 3.6+
- Instalar dependências listadas no arquivo `requirements.txt`
- Adicionar o .env no projeto (Solicitar para o Samuel no wpp o arquivo que contém o token para realizar a transcrição).

## Instalação

1. Clone o repositório para o seu ambiente local:
    ```bash
    git clone https://github.com/samuel-vieira-dev/youtube-ads-scraper.git
    ```
   
2. Navegue para o diretório do projeto:
    ```bash
    cd youtube-ads-scraper
    ```

3. Crie um ambiente virtual:
    ```bash
    python -m venv venv
    ```
    
4. Ative o ambiente virtual:
- No Windows:
    ```bash
    venv\Scripts\activate
    ```
- No Mac:
    ```bash
    source venv/bin/activate
    ```

5. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Uso
1. Execute o script principal:
    ```bash
    python main.py
    ```

2. Insira os domínios ou landing pages quando solicitado no terminal, separados por vírgulas.

3. Insira o número máximo de vídeos que deseja buscar (entre 1 e 10). Limitei a esse número pois estou usando o Whisper da OpenAI pra realizar a transcrição. Ele cobra por uso.
