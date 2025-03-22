import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys
import re
import time
import threading

# Global event to signal threads to stop
stop_event = threading.Event()

def handler(signum, frame):
    print("\n🛑 Ctrl+C detected. Stopping now...")
    stop_event.set()  # signal threads to stop
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handler)
cities = pd.read_csv("cities.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0"
}

ban_keywords = [
    "translate", "wikipedia:", "edit", "interlanguage", "summary", "talk",
    "copyright", "template", "module", "page", "portal", "wikidata", "contact",
    "random", "file", "special", "donate", "main page", "search", "tourism in",
    "list of tourist", "development project", "deepl", "google translate",
    "copyright attribution", "edit summary", "website", "log in or create an account", "request the creation of a new category",
    "try the purge function", "redirect", "check thedeletion log"
]
ban_pattern = re.compile("|".join(ban_keywords), re.IGNORECASE)

session = requests.Session()
session.headers.update(HEADERS)

def clean_title(title):
    return title.strip().split('(')[0].replace("\xa0", " ")

def try_scrape(url, city, country):
    # Check for stop event early
    if stop_event.is_set():
        return []
    try:
        res = session.get(url, timeout=5)
        if "Wikipedia does not have an article with this exact name" in res.text:
            return []

        soup = BeautifulSoup(res.content, "lxml")
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div:
            return []

        lis = content_div.select("ul > li > a")
        places = []
        added = set()

        for i, link in enumerate(lis):
            if stop_event.is_set():
                break
            if i >= 30:
                break
            name = link.get_text(strip=True)
            if len(name) < 3:
                continue
            if ban_pattern.search(name):
                continue
            name = clean_title(name)
            if name in added:
                continue
            added.add(name)
            places.append({
                "city": city,
                "country_name": country,
                "place_name": name
            })
            if len(places) == 10:
                break
        return places

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def process_city(row):
    if stop_event.is_set():
        return []
    city = row["name"]
    country = row["country_name"]
    print(f"Scraping: {city}")
    city_encoded = urllib.parse.quote(city)
    urls = [
        f"https://en.wikipedia.org/wiki/List_of_tourist_attractions_in_{city_encoded}",
        f"https://en.wikipedia.org/wiki/Tourism_in_{city_encoded}",
        f"https://en.wikipedia.org/wiki/Category:Tourist_attractions_in_{city_encoded}"
    ]
    for url in urls:
        if stop_event.is_set():
            break
        places = try_scrape(url, city, country)
        if places:
            return places
    return []

all_places = []
start_time = time.time()

try:
    print("🚀 Starting multithreaded scraper with improved signal handling...\n")
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(process_city, row) for _, row in cities.iterrows()]
        for future in as_completed(futures):
            if stop_event.is_set():
                break
            result = future.result()
            if result:
                all_places.extend(result)

except KeyboardInterrupt:
    print("\n🛑 Interrupted by user (Ctrl+C). Saving progress...")

finally:
    if all_places:
        df = pd.DataFrame(all_places).drop_duplicates()
        df.to_csv("popular_city_attractions.csv", index=False)
        elapsed = time.time() - start_time
        print(f"💾 Saved to 'popular_city_attractions.csv' in {elapsed:.2f} seconds")
    else:
        print("⚠️ No data scraped.")
