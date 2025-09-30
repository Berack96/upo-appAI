from .base import BaseWrapper
from .coinbase import CoinBaseWrapper
from .binance import BinanceWrapper
from .cryptocompare import CryptoCompareWrapper
from app.utils.wrapper_handler import WrapperHandler

__all__ = [ "MarketAPIs", "BinanceWrapper", "CoinBaseWrapper", "CryptoCompareWrapper" ]


# TODO se si vuole usare un aggregatore di dati di mercato, si può aggiungere qui facendo una classe extra (simile a questa) che per ogni chiamata chiama tutti i wrapper e aggrega i risultati
class MarketAPIs(BaseWrapper):
    """
    Classe per gestire le API di mercato disponibili.
    Permette di ottenere un'istanza della prima API disponibile in base alla priorità specificata.
    Supporta operazioni come ottenere informazioni su singoli prodotti, liste di prodotti e dati storici.
    Usa un WrapperHandler per gestire più wrapper e tentare chiamate in modo resiliente.
    """

    def __init__(self, currency: str = "USD"):
        self.currency = currency
        wrappers = [ CoinBaseWrapper, CryptoCompareWrapper ]
        self.wrappers: WrapperHandler[BaseWrapper] = WrapperHandler.build_wrappers(wrappers)

    def get_product(self, asset_id):
        return self.wrappers.try_call(lambda w: w.get_product(asset_id))
    def get_products(self, asset_ids: list):
        return self.wrappers.try_call(lambda w: w.get_products(asset_ids))
    def get_all_products(self):
        return self.wrappers.try_call(lambda w: w.get_all_products())
    def get_historical_prices(self, asset_id = "BTC", limit: int = 100):
        return self.wrappers.try_call(lambda w: w.get_historical_prices(asset_id, limit))
