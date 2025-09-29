#### FOR ALL FILES OUTSIDE src/ FOLDER ####
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
###########################################

from dotenv import load_dotenv
from app.markets.cryptocompare import CryptoCompareWrapper

def main():
    print("Demo CryptoCompare")

    print("=== Chiavi API ===")
    print(f"  CRYPTOCOMPARE_API_KEY: {os.getenv('CRYPTOCOMPARE_API_KEY') is not None}")

    # Inizializza le API
    cryptocompare = CryptoCompareWrapper()

    # ottenimento prezzo attuale
    print("=== Demo prezzo attuale ===")
    test_symbols = ["BTC", "ETH", "ADA"]
    for symbol in test_symbols:
        info = cryptocompare.get_product(symbol)
        print(f"  {symbol}: ${info.price:,.2f}")

    # ottenimento prezzi storici
    print("=== Demo prezzi storici ===")
    test_symbols = ["BTC", "ETH"]
    for symbol in test_symbols:
        prices = cryptocompare.get_historical_prices(symbol)
        prices = [f'[${entry.high:,.2f}-${entry.low:,.2f}]' for entry in prices]
        print(f"  {symbol}: {" ".join(prices[:5])}") # mostra solo i primi 5

if __name__ == "__main__":
    load_dotenv()
    main()