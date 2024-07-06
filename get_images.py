from pathlib import Path

import requests
from bs4 import BeautifulSoup, ResultSet, Tag

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
    with open(ARQ_CHAR, "r") as characters:
        for character in characters:
            pasta = ROOT / character.strip("\n")
            pasta.mkdir(exist_ok=True)


get_characters()
create_directories()
