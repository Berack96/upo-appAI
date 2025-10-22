from dotenv import load_dotenv
from app.api.tools import NewsAPIsTool

def main():
    api = NewsAPIsTool()
    articles_aggregated = api.get_latest_news_aggregated(query="bitcoin", limit=2)
    for provider, articles in articles_aggregated.items():
        print("===================================")
        print(f"Provider: {provider}")
        for article in articles:
            print(f"== [{article.time}] {article.title} ==")
            print(f"   {article.description}")

if __name__ == "__main__":
    load_dotenv()
    main()
