import json
from agno.tools.yfinance import YFinanceTools
from app.api.core.markets import MarketWrapper, ProductInfo, Price


def extract_product(stock_data: dict[str, str]) -> ProductInfo:
    """
    Converte i dati di YFinanceTools in ProductInfo.
    """
    product = ProductInfo()
    product.id = stock_data.get('Symbol', '')
    product.symbol = product.id.split('-')[0]  # Rimuovi il suffisso della valuta per le crypto
    product.price = float(stock_data.get('Current Stock Price', f"0.0 USD").split(" ")[0]) # prende solo il numero
    product.volume_24h = 0.0 # YFinance non fornisce il volume 24h direttamente
    product.currency = product.id.split('-')[1]  # La valuta è la parte dopo il '-'
    return product

def extract_price(hist_data: dict[str, str]) -> Price:
    """
    Converte i dati storici di YFinanceTools in Price.
    """
    timestamp = int(hist_data.get('Timestamp', '0'))

    price = Price()
    price.high = float(hist_data.get('High', 0.0))
    price.low = float(hist_data.get('Low', 0.0))
    price.open = float(hist_data.get('Open', 0.0))
    price.close = float(hist_data.get('Close', 0.0))
    price.volume = float(hist_data.get('Volume', 0.0))
    price.set_timestamp(timestamp_ms=timestamp)
    return price


class YFinanceWrapper(MarketWrapper):
    """
    Wrapper per YFinanceTools che fornisce dati di mercato per azioni, ETF e criptovalute.
    Implementa l'interfaccia BaseWrapper per compatibilità con il sistema esistente.
    Usa YFinanceTools dalla libreria agno per coerenza con altri wrapper.
    """

    def __init__(self, currency: str = "USD"):
        self.currency = currency
        self.tool = YFinanceTools()

    def _format_symbol(self, asset_id: str) -> str:
        """
        Formatta il simbolo per yfinance.
        Per crypto, aggiunge '-' e la valuta (es. BTC -> BTC-USD).
        """
        i = asset_id.find('-')
        if i != -1: asset_id = asset_id[:i]
        return f"{asset_id}-{self.currency}"

    def get_product(self, asset_id: str) -> ProductInfo:
        symbol = self._format_symbol(asset_id)
        stock_info = self.tool.get_company_info(symbol)
        stock_info = json.loads(stock_info)
        return extract_product(stock_info)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        products: list[ProductInfo] = []
        for asset_id in asset_ids:
            product = self.get_product(asset_id)
            products.append(product)
        return products

    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[Price]:
        symbol = self._format_symbol(asset_id)

        days = limit // 24 + 1  # Arrotonda per eccesso
        hist_data = self.tool.get_historical_stock_prices(symbol, period=f"{days}d", interval="1h")
        hist_data = json.loads(hist_data)

        # Il formato dei dati è {timestamp: {Open: x, High: y, Low: z, Close: w, Volume: v}}
        timestamps = sorted(hist_data.keys())[-limit:]

        prices: list[Price] = []
        for timestamp in timestamps:
            temp = hist_data[timestamp]
            temp['Timestamp'] = timestamp
            price = extract_price(temp)
            prices.append(price)
        return prices
