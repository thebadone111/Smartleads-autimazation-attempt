import requests
import re
from bs4 import BeautifulSoup
from analytics import logger

def get_html(url):
    try:
        result = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    except Exception as e:
        logger.error(f"Problem with get request, probably didn't find email: {e}")
        return None
    return result.text

def get_text(txt):
    soup = BeautifulSoup(txt, "html.parser")
    text = soup.get_text()
    return text

def long_to_short(long_string, max_length):
    # Split the long string into multiple strings
    split_strings = []
    while len(long_string) > max_length:
        # Find the index of the last space before the maximum length
        split_index = long_string[:max_length].rfind(' ')
        # If no space is found, split at the maximum length
        if split_index == -1:
            split_index = max_length
        # Add the split string to the list
        split_strings.append(long_string[:split_index])
        # Remove the split string from the long string
        long_string = long_string[split_index+1:]
    # Add the last part of the long string to the list (split_strings[0])
    split_strings.append(long_string)
    return split_strings

def main(domain, max_length = 3000):
    logger.info(f"Scraping website: {domain}")
    html = get_html(domain)
    if html == None:
        return None
    text = get_text(html)
    #text_list = long_to_short(text, max_length)
    return text