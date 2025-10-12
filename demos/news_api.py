#### FOR ALL FILES OUTSIDE src/ FOLDER ####
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
###########################################

from dotenv import load_dotenv
from app.api.news import NewsApiWrapper

def main():
    api = NewsApiWrapper()
    articles = api.get_latest_news(query="bitcoin", limit=5)
    assert len(articles) > 0
    print("ok")

if __name__ == "__main__":
    load_dotenv()
    main()