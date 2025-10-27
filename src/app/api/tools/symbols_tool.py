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
    Classe per ottenere i simboli delle criptovalute tramite Yahoo Finance.
    """

    def __init__(self, cache_file: str = 'resources/cryptos.csv'):
        self.cache_file = cache_file
        self.final_table = pd.read_csv(self.cache_file) if os.path.exists(self.cache_file) else pd.DataFrame() # type: ignore
        Toolkit.__init__(self, # type: ignore
            name="Crypto Symbols Tool",
            instructions="Tool to get cryptocurrency symbols and search them by name.",
            tools=[
                self.get_all_symbols,
                self.get_symbols_by_name,
            ],
        )

    def get_all_symbols(self) -> list[str]:
        """
        Restituisce tutti i simboli delle criptovalute.
        Returns:
            list[str]: Lista di tutti i simboli delle criptovalute.
        """
        return self.final_table['Symbol'].tolist() if not self.final_table.empty else []

    def get_symbols_by_name(self, query: str) -> list[tuple[str, str]]:
        """
        Cerca i simboli che contengono la query.
        Args:
            query (str): Query di ricerca.
        Returns:
            list[tuple[str, str]]: Lista di tuple (simbolo, nome) che contengono la query.
        """
        query_lower = query.lower()
        positions = self.final_table['Name'].str.lower().str.contains(query_lower)
        return self.final_table[positions][['Symbol', 'Name']].apply(tuple, axis=1).tolist()

    async def fetch_crypto_symbols(self, force_refresh: bool = False) -> None:
        """
        Recupera tutti i simboli delle criptovalute da Yahoo Finance e li memorizza in cache.
        Args:
            force_refresh (bool): Se True, forza il recupero anche se i dati sono già in cache.
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
