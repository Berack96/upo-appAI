import os
import httpx
import asyncio
import logging
import pandas as pd
from io import StringIO
from agno.tools.toolkit import Toolkit

logging.basicConfig(level=logging.INFO)
logging = logging.getLogger("crypto_symbols")



BASE_URL = "https://finance.yahoo.com/markets/crypto/all/"


class CryptoSymbolsTools(Toolkit):
    """
    Class for obtaining cryptocurrency symbols via Yahoo Finance.
    (This class-level docstring is for developers).
    """

    def __init__(self, cache_file: str = 'resources/cryptos.csv'):
        self.cache_file = cache_file
        try:
            self.final_table = pd.read_csv(self.cache_file) if os.path.exists(self.cache_file) else pd.DataFrame(
                columns=['Symbol', 'Name'])
        except Exception:
            self.final_table = pd.DataFrame(columns=['Symbol', 'Name'])

        Toolkit.__init__(self,  # type: ignore
                         name="Crypto Symbols Tool",
                         instructions="A utility tool to find and verify the correct cryptocurrency symbols (tickers). " \
                                      "Use this to translate a cryptocurrency name (e.g., 'Bitcoin') into its official symbol " \
                                      "(e.g., 'BTC-USD') *before* delegating tasks to the MarketAgent.",
                         tools=[
                             self.get_all_symbols,
                             self.get_symbols_by_name,
                         ],
                         )

    def get_all_symbols(self) -> list[str]:
        """
        Returns a complete list of all available cryptocurrency symbols (tickers).

        Warning: This list can be very long. Prefer 'get_symbols_by_name'
        if you are searching for a specific asset.

        Returns:
            list[str]: A comprehensive list of all supported crypto symbols (e.g., "BTC-USD", "ETH-USD").
        """
        return self.final_table['Symbol'].tolist() if not self.final_table.empty else []

    def get_symbols_by_name(self, query: str) -> list[tuple[str, str]]:
        """
        Searches the cryptocurrency database for assets matching a name or symbol.

        Use this to find the exact, correct symbol for a cryptocurrency name.
        (e.g., query="Bitcoin" might return [("BTC-USD", "Bitcoin USD")]).

        Args:
            query (str): The name, partial name, or symbol to search for (e.g., "Bitcoin", "ETH").

        Returns:
            list[tuple[str, str]]: A list of tuples, where each tuple contains
                                  the (symbol, full_name) of a matching asset.
                                  Returns an empty list if no matches are found.
        """
        if self.final_table.empty or 'Name' not in self.final_table.columns or 'Symbol' not in self.final_table.columns:
            return []

        try:
            # Cerca sia nel nome che nel simbolo, ignorando maiuscole/minuscole
            mask = self.final_table['Name'].str.contains(query, case=False, na=False) | \
                   self.final_table['Symbol'].str.contains(query, case=False, na=False)

            filtered_df = self.final_table[mask]

            # Converte il risultato in una lista di tuple
            return list(zip(filtered_df['Symbol'], filtered_df['Name']))
        except Exception:
            return []

    async def fetch_crypto_symbols(self, force_refresh: bool = False) -> None:
        """
        It retrieves all cryptocurrency symbols from Yahoo Finance and caches them.
        Args:
            force_refresh (bool): If True, it forces the retrieval even if the data are already in the cache.
        """
        if not force_refresh and not self.final_table.empty:
            return

        num_currencies = 250 # It looks like this is the max per page otherwise yahoo returns 26
        offset = 0
        stop = not self.final_table.empty
        table = self.final_table.copy()

        while not stop:
            text = await self.___request(offset, num_currencies)
            tables = pd.read_html(text) # type: ignore
            df = tables[0]
            df.columns = table.columns if not table.empty else df.columns
            table = pd.concat([table, df], ignore_index=True)

            total_rows = df.shape[0]
            offset += total_rows
            if total_rows < num_currencies:
                stop = True

        table.dropna(axis=0, how='all', inplace=True) # type: ignore
        table.dropna(axis=1, how='all', inplace=True) # type: ignore
        table.to_csv(self.cache_file, index=False)
        self.final_table = table

    async def ___request(self, offset: int, num_currencies: int) -> StringIO:
        while True:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{BASE_URL}?start={offset}&count={num_currencies}", headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 429: # Too many requests
                    secs = int(resp.headers.get("Retry-After", 2))
                    logging.warning(f"Rate limit exceeded, waiting {secs}s before retrying...")
                    await asyncio.sleep(secs)
                    continue
                if resp.status_code != 200:
                    logging.error(f"Error fetching crypto symbols: [{resp.status_code}] {resp.text}")
                    break
                return StringIO(resp.text)
        return StringIO("")



if __name__ == "__main__":
    crypto_symbols = CryptoSymbolsTools()
    asyncio.run(crypto_symbols.fetch_crypto_symbols(force_refresh=True))
