from dotenv import load_dotenv
from app.api.tools import MarketAPIsTool

def main():
    api = MarketAPIsTool()
    prices_aggregated = api.get_historical_prices_aggregated("BTC", limit=5)
    for price in prices_aggregated:
        print(f"== [{price.timestamp}] {price.low:.2f} - {price.high:.2f} ==")

if __name__ == "__main__":
    load_dotenv()
    main()
