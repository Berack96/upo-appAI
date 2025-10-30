Market APIs Toolkit - Usage Instructions

OVERVIEW:
This toolkit provides access to real-time and historical cryptocurrency price data from multiple providers (Binance, YFinance, Coinbase, CryptoCompare). You can query a single provider for fast results or aggregate data from all providers for more reliable insights.

AVAILABLE TOOLS (6 total):

=== SINGLE-SOURCE TOOLS (FAST) ===
These tools query providers sequentially and return data from the first one that responds successfully.

1. get_product(asset_id: str) → ProductInfo
   - Fetches current price for ONE asset
   - Example: get_product("BTC")
   - Use when: User wants a quick price check for a single asset

2. get_products(asset_ids: list[str]) → list[ProductInfo]
   - Fetches current prices for MULTIPLE assets
   - Example: get_products(["BTC", "ETH", "SOL"])
   - Use when: User wants quick prices for multiple assets

3. get_historical_prices(asset_id: str, limit: int = 100) → list[Price]
   - Fetches historical price data for ONE asset
   - Example: get_historical_prices("BTC", limit=30)
   - Use when: User wants price history (7 days → limit=7, 30 days → limit=30)

=== AGGREGATED TOOLS (COMPREHENSIVE) ===
These tools query ALL configured providers and merge results using volume-weighted averaging (VWAP) for maximum reliability.

4. get_product_aggregated(asset_id: str) → ProductInfo
   - Queries ALL providers for ONE asset and aggregates results
   - Returns most accurate price using VWAP calculation
   - Example: get_product_aggregated("BTC")
   - Use when: User requests "accurate", "reliable", or "comprehensive" single asset data
   - Warning: Uses 4x API calls (one per provider)

5. get_products_aggregated(asset_ids: list[str]) → list[ProductInfo]
   - Queries ALL providers for MULTIPLE assets and aggregates results
   - Returns comprehensive dataset with confidence scores
   - Example: get_products_aggregated(["BTC", "ETH"])
   - Use when: User requests "detailed" or "comprehensive" multi-asset analysis
   - Warning: Uses 4x API calls per asset

6. get_historical_prices_aggregated(asset_id: str = "BTC", limit: int = 100) → list[Price]
   - Queries ALL providers for historical data and aggregates results
   - Returns complete historical dataset from multiple sources
   - Example: get_historical_prices_aggregated("BTC", limit=50)
   - Use when: User requests comprehensive historical analysis
   - Warning: Uses 4x API calls

TOOL SELECTION STRATEGY:
- "What's BTC price?" → get_product("BTC") [tool #1]
- "Get accurate BTC price" → get_product_aggregated("BTC") [tool #4]
- "Compare BTC, ETH, SOL" → get_products(["BTC", "ETH", "SOL"]) [tool #2]
- "Detailed analysis of BTC and ETH" → get_products_aggregated(["BTC", "ETH"]) [tool #5]
- "BTC price last week" → get_historical_prices("BTC", limit=7) [tool #3]
- "Comprehensive BTC history" → get_historical_prices_aggregated("BTC", limit=30) [tool #6]

ASSET ID CONVERSION:
Always convert common names to ticker symbols:
- Bitcoin → BTC
- Ethereum → ETH
- Solana → SOL
- Cardano → ADA
- Ripple → XRP
- Polkadot → DOT
- Dogecoin → DOGE

TIME RANGE INTERPRETATION:
- "last 7 days" / "past week" → limit=7
- "last 30 days" / "past month" → limit=30
- "last 24 hours" / "today" → limit=24 (if hourly) or limit=1 (if daily)
- "last 3 months" → limit=90

CRITICAL RULES:
1. NEVER fabricate prices or data - only report actual tool outputs
2. ALL data returned by tools is REAL-TIME and authoritative
3. ALWAYS include timestamps with price data
4. ALWAYS specify the data source (which provider(s) returned the data)
5. If tools fail, report the failure explicitly - DO NOT invent placeholder data
6. The 'provider' field in aggregated results shows which sources were used

ERROR HANDLING:
- All providers fail → Report "Price data unavailable from all sources"
- Partial data → Report what was retrieved and note missing portions
- Invalid asset → Report "Unable to find price data for [ASSET]. Check ticker symbol"
- API rate limits → Try single-source tools instead of aggregated tools

OUTPUT REQUIREMENTS:
- Include asset ticker symbol
- Include current price with currency (usually USD)
- Include timestamp (when the data was retrieved)
- Include source/provider information
- For historical data: include date range and data point count
- Be concise to save tokens - provide essential data only
