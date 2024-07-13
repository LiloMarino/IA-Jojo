""" Alternativa para obtenção dos links """

import json
import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

CHAR_LIST = Path("characters.txt")
LINKS_JSON = "links.json"
WAIT_TIME = 5
SLEEP_TIME = 1.5


def save_links(links: dict[str, list]):
    """
    Salva os links no json

    Args:
        links (dict): Dicionário dos links
    """
    with open(LINKS_JSON, "w", encoding="utf-8") as json_file:
        json.dump(links, json_file, indent=4)


def load_links() -> dict:
    """
    Carrega os links do json

    Returns:
        dict: Retorna o dicionário de links
    """
    if os.path.exists(LINKS_JSON):
        with open(LINKS_JSON, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    else:
        return {}


def fetch_image_links(
    links: dict[str, list],
    wd: WebDriver,
    query: str,
    aditional_query: str,
    limit: int = 20,
    offset: int = 0,
):
    """
    Busca os links das imagens

    Args:
        links (dict[str, list]): Dicionário dos links
        query (str): Termo Pesquisado
        limit (int, optional): Limite de links. Defaults to 20.
        offset (int, optional): Links que serão ignorados/pulados. Defaults to 0.
    """
    search_url = (
        f"https://www.google.com/search?hl=en&q={query + aditional_query}&tbm=isch"
    )
    wd.get(search_url)
    image_links = set()
    if query in links:
        image_links = set(links[query])
    image_count = 0
    layout_xpath = '//*[@id="rso"]/div/div/div[1]/div/div/div'
    img_xpath = (
        '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img'
    )
    while image_count < limit:
        thumbnail_results = WebDriverWait(wd, WAIT_TIME).until(
            lambda x: x.find_elements(By.XPATH, layout_xpath)
        )
        number_results = len(thumbnail_results)
        for img in thumbnail_results[offset:number_results]:
            try:
                img.click()
                time.sleep(SLEEP_TIME)
            except Exception as e:
                print(e)
                continue
            try:
                actual_images = WebDriverWait(wd, WAIT_TIME).until(
                    lambda x: x.find_elements(
                        By.XPATH,
                        img_xpath,
                    )
                )
            except TimeoutException:
                continue

            for image in actual_images:
                if "encrypted" not in image.get_attribute("src"):
                    image_links.add(image.get_attribute("src"))
                    break

            image_count = len(image_links)

            if len(image_links) >= limit:
                break

        links[query] = list(image_links)
        save_links(links)


links_dict = load_links()
with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.maximize_window()
    with open(CHAR_LIST, "r", encoding="utf-8") as character_list:
        for line in character_list:
            character_name = line.strip()
            fetch_image_links(links_dict, driver, character_name, " Jojo")
save_links(links_dict)
