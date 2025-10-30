# Market APIs - Instructions

## Tools (6)
**Single-source (fast):** First available provider
1. `get_product(asset_id)` - Current price, 1 asset
2. `get_products(asset_ids)` - Current prices, multiple assets
3. `get_historical_prices(asset_id, limit=100)` - Price history, 1 asset

**Aggregated (accurate):** All providers, VWAP calculation
4. `get_product_aggregated(asset_id)` - Accurate price, 1 asset (4x API calls)
5. `get_products_aggregated(asset_ids)` - Accurate prices, multiple (4x per asset)
6. `get_historical_prices_aggregated(asset_id, limit=100)` - Historical, all sources (4x calls)

## Selection Strategy
- Quick check → single-source (tools 1-3)
- Keywords "accurate", "reliable", "comprehensive" → aggregated (tools 4-6)

## Key Mappings
**Assets:** Bitcoin→BTC, Ethereum→ETH, Solana→SOL, Cardano→ADA, Ripple→XRP, Polkadot→DOT, Dogecoin→DOGE
**Time:** "7 days"→limit=7, "30 days"→limit=30, "24h"→limit=24, "3 months"→limit=90

## Critical Rules
- Never fabricate data - only report actual tool outputs
- Include: ticker, price+currency, timestamp, provider source
- Failure handling: Report explicit error, no placeholder data
- Be concise to save tokens
