import requests
from bs4 import BeautifulSoup
import subprocess
import random

def get_description(query):
    html = requests.get("https://www.shutterstock.com/search?searchterm="+query).text
    soup = BeautifulSoup(html, "html.parser")
    description = random.choice(soup.select(".description"))
    return description.text.strip()


if __name__ == '__main__':
    print(get_description("baby"))
