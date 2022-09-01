# The only library you'll need to install is Beautiful Soup 4 (use: "pip install beautifulsoup4").
from bs4 import BeautifulSoup as bs

# The last three libraries are from the python standard library.
import requests     # To make web requests
import time         # To measure time
import json         # To handle json files
import re           # To use regular expressions
import concurrent.futures

def get_songs_list(artist_url: str) -> list[str]:
    """
    Returns a list with all the songs urls of a given artist

    Args:
        artist_url (str): Artist url rfom letras.com

    Returns:
        list[str]: A list containing the songs urls as strings
    """

    url = artist_url + 'mais_acessadas.html'    # Required for this web
    page = requests.get(url)

    # Parsing web content with BeautifulSoup
    soup = bs(page.content, 'html.parser')
    # Looking for al the 'li' items with 'cnt-list-row' class in the html
    songs_items = soup.find_all('li', class_='cnt-list-row')

    # For every "li" item, we extract the "data-shareurl" tag inside
    songs_urls = [song.get("data-shareurl") for song in songs_items]

    return songs_urls


def get_lyrics_from_url(song_url: str, breaklines=False) -> str:
    """
    Extract the lyrics of a song page

    Args:
        song_url (str): Url of a song

    Returns:
        str: The lyrics of the given song's url
    """    

    song = requests.get(song_url)
    song = bs(song.content, 'html.parser')
    lyric_div = song.find('div', class_='cnt-letra')
    parrafos = lyric_div.find_all('p')

    lyric = ""

    if breaklines:
        for parrafo in parrafos:
            text = str(parrafo)
            text = text.replace("<br>", "\n")
            text = text.replace("<br/>", "\n")
            text = text.replace("</br>", "")
            text = text.replace("<p>", "")
            text = text.replace("</p>", "\n")
            lyric += text + "\n"

        lyric = lyric[:-2] # Remove extra \n
    
    else:
        # We use regex to extract and clean the lyrics
        for parrafo in parrafos:

            # Alternartive to get lyrics without breaklines
            # Separate camelCase words (e.g. camelCase -> camel Case)
            lyric += re.sub(r"\B([A-Z])", r" \1", parrafo.text) + " "
            
            # Remove extra spaces
            lyric = re.sub(' +', ' ', lyric)
            lyric += " "
    
    return lyric


def get_lyrics_from_div(div, breaklines:bool =False) -> str:
    """
    Extract the lyrics of a div

    Args:
        div (bs.element.Tag): div tag containing the lyrics

    Returns:
        str: The lyrics of the given song
    """

    parrafos = div.find_all('p')

    lyric = ""

    if breaklines:
        for parrafo in parrafos:
            text = str(parrafo)
            text = text.replace("<br>", "\n")
            text = text.replace("<br/>", "\n")
            text = text.replace("</br>", "")
            text = text.replace("<p>", "")
            text = text.replace("</p>", "\n")
            lyric += text + "\n"

        lyric = lyric[:-2] # Remove extra \n
    
    else:
        # We use regex to extract and clean the lyrics
        for parrafo in parrafos:
            # Alternartive to get lyrics without breaklines
            # Separate camelCase words (e.g. camelCase -> camel Case)
            lyric += re.sub(r"\B([A-Z])", r" \1", parrafo.text) + " "
            
            # Remove extra spaces
            lyric = re.sub(' +', ' ', lyric)
    
    return lyric


def get_song_info(song_url: str) -> dict:
    """
    Returns a dictionary containing important information of a song, such as
    its name, lyrics and url
    
    Args:
        song_url (str): url of song

    Returns:
        dict: Dictionary with the song info
    """

    song = requests.get(song_url)
    song = bs(song.content, 'html.parser')

    # Getting the song name
    song_name = song.find("div", class_="cnt-head_title").find("h1").text

    # Getting song lyrics
    lyric_div = song.find('div', class_='cnt-letra')
    lyrics = get_lyrics_from_div(lyric_div)
    
    # Returning result dict
    return {
        "name": song_name,
        "lyrics": lyrics,
        "url": song_url
    }


def get_artist_songs(artist_url: str) -> list[dict]:
    """
    Returns name, lyrics and url of every song of an artist url in JSON format
    
    Args:
        artist_url (str): letras.com main page artist url

    Returns:
        list[dict]: List of dictionary with the info (JSON format)
    """
    urls = get_songs_list(artist_url)

    data = [get_song_info(url) for url in urls]
    return data


def scrap_songs_concurrently(artist_url: str, output_name: str) -> int:
    """
    Creates a json file with the songs info of an artist.
    Returns the number of songs scrapped.

    Args:
        artist_url (str): letras.com main page artist url
        output_name (str): name of created json file

    Returns:
        int: Number of songs scrapped.
    """
    
    songs_urls = get_songs_list(artist_url)
    songs_info = [get_song_info(url) for url in songs_urls]

    with open(f"{output_name}.json", "w") as fp:
        json.dump(songs_info, fp, indent=4)

    return len(songs_info)


def scrap_songs_threading(artist_url: str, output_name: str) -> int:
    """
    Creates a json file with the songs info of an artist using multithreading.
    Returns the number of songs scrapped.

    Args:
        artist_url (str): letras.com main page artist url
        output_name (str): name of created json file

    Returns:
        int: Number of songs scrapped.
    """

    songs_urls = get_songs_list(artist_url)
    # songs_info = []

    # def insert_song_info(url):
    #     songs_info.append(get_song_info(url))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(get_song_info, songs_urls)

        songs_info = [result for result in results]

    with open(f"{output_name}.json", "w") as fp:
        json.dump(songs_info, fp, indent=4)

    return len(songs_info)


