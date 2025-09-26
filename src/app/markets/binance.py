# Versione pubblica senza autenticazione
from binance.client import Client

class PublicBinanceAgent:
    def __init__(self):
        # Client pubblico (senza credenziali)
        self.client = Client()

    def get_public_prices(self):
        """Ottiene prezzi pubblici"""
        try:
            btc_price = self.client.get_symbol_ticker(symbol="BTCUSDT")
            eth_price = self.client.get_symbol_ticker(symbol="ETHUSDT")

            return {
                'BTC_USD': float(btc_price['price']),
                'ETH_USD': float(eth_price['price']),
                'source': 'binance_public'
            }
        except Exception as e:
            print(f"Errore: {e}")
            return None

# Uso senza credenziali
public_agent = PublicBinanceAgent()
public_prices = public_agent.get_public_prices()
print(public_prices)
