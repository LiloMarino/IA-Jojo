import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

ROOT = Path("Characters")
ARQ_CHAR = Path("characters.txt")


def get_characters():
    """
    Obtém a lista de personagens pela página do MyAnimesList
    """
    url = input("Cole o link da página de personagens do MyAnimesList:")
    response = requests.get(url)
    parsed_html = BeautifulSoup(response.content, "html.parser")
    characters_names: ResultSet[Tag] = parsed_html.find_all(
        "h3", class_="h3_character_name"
    )
    with open(ARQ_CHAR, "w", encoding="utf-8") as characters:
        for character_name in characters_names:
            character_name
            characters.write(
                character_name.text.replace(",", "").replace(" ", "_").replace(".", "")
                + "\n"
            )


def create_directories():
    """
    Cria todos os diretórios necessários separando por personagem
    """
    ROOT.mkdir(exist_ok=True)
    with open(ARQ_CHAR, "r", encoding="utf-8") as characters:
        for character in characters:
            pasta = ROOT / character.strip()
            pasta.mkdir(exist_ok=True)


def fetch_image_urls(
    query, max_links_to_fetch, wd: WebDriver, sleep_between_interactions=1
):
    """
    Busca URLs de imagens de personagens usando o Google Imagens
    """
    search_url = f"https://www.google.com/search?hl=en&q={query}&tbm=isch"

    wd.get(search_url)

    image_urls = set()
    image_count = 0
    results_start = 0

    while image_count < max_links_to_fetch:
        thumbnail_results = wd.find_elements(
            By.XPATH, '//*[@id="rso"]/div/div/div[1]/div/div/div'
        )
        number_results = len(thumbnail_results)

        for img in thumbnail_results[results_start:number_results]:
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            actual_image = wd.find_element(
                By.XPATH,
                '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]',
            )
            if actual_image.get_attribute(
                "src"
            ) and "http" in actual_image.get_attribute("src"):
                image_urls.add(actual_image.get_attribute("src"))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                break
        else:
            time.sleep(1)
            load_more_button = wd.find_element(By.CSS_SELECTOR, ".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        results_start = len(thumbnail_results)

    return list(image_urls)


def download_image(url, filepath):
    """
    Baixa uma imagem da URL especificada e salva no caminho fornecido
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, "wb") as file:
                for chunk in response:
                    file.write(chunk)
    except Exception as e:
        print(f"Não foi possível baixar a imagem {url}: {e}")


def download_images():
    """
    Baixa imagens para cada personagem e salva nas pastas correspondentes
    """
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as wd:
        with open(ARQ_CHAR, "r", encoding="utf-8") as characters:
            for character in characters:
                character = character.strip()
                character_path = ROOT / character

                # Verifica se a pasta já contém 20 imagens
                if len(list(character_path.glob("*.jpg"))) >= 20:
                    print(f"A pasta para {character} já contém 20 imagens, pulando...")
                    continue

                image_urls = fetch_image_urls(f"Jojo {character.replace("_", " ")}", 20, wd)
                for i, url in enumerate(image_urls):
                    filepath = character_path / f"{character}_{i+1}.jpg"
                    download_image(url, filepath)
                    time.sleep(1)  # Para evitar sobrecarga de solicitações


get_characters()
create_directories()
download_images() # <-- Instável
