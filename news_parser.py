import requests
from bs4 import BeautifulSoup

def get_tech_news():
    """Scrapes the top 10 headlines from Hacker News."""
    url = "https://news.ycombinator.com/"
    try:
        # Adding a User-Agent to look like a real browser
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []
        
        # Hacker News specific tags for titles
        items = soup.find_all('span', class_='titleline')
        
        for item in items[:10]: # Limit to top 10
            link = item.find('a')
            if link:
                headlines.append(link.text)
        
        return headlines
    except Exception as e:
        print(f"Scraping error: {e}")
        return []