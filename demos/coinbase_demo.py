#### FOR ALL FILES OUTSIDE src/ FOLDER ####
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
###########################################

from dotenv import load_dotenv
from app.markets import CoinBaseWrapper

def main():
    print("Demo Coinbase CDP")

    print("=== Chiavi API ===")
    print(f"  COINBASE_API_KEY: {os.getenv('COINBASE_API_KEY') is not None}")
    print(f"  COINBASE_API_SECRET: {os.getenv('COINBASE_API_SECRET') is not None}")

    # Inizializza le API
    coinbase = CoinBaseWrapper()

    # ottenimento prezzo attuale
    print("=== Demo prezzo attuale ===")
    test_symbols = ["BTC", "ETH", "ADA"]
    for symbol in test_symbols:
        info = coinbase.get_product(symbol)
        print(f"  {symbol}: ${info.price:,.2f}")

    # ottenimento prezzi storici
    print("\n=== Demo prezzi storici ===")
    test_symbols = ["BTC", "ETH"]
    for symbol in test_symbols:
        prices = coinbase.get_historical_prices(symbol)
        print(f"  {symbol}: {" ".join([f'${entry["price"]:,.2f}' for entry in prices[:5]])}") # mostra solo i primi 5

if __name__ == "__main__":
    load_dotenv()
    main()
