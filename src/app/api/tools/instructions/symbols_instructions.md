# Crypto Symbols Tool - Instructions

## Purpose
Cryptocurrency symbol lookup and name-based search using cached Yahoo Finance database.

## Tools (2)

### 1. `get_all_symbols()` → list[str]
Returns all available cryptocurrency symbols from cache. No API calls, instant response.

**Returns:** List like `["BTC-USD", "ETH-USD", "SOL-USD", ...]` (~1,500+ symbols)

**Use Cases:**
- Verify symbol availability before API call
- List all supported cryptocurrencies
- Validate user input against known symbols

### 2. `get_symbols_by_name(query: str)` → list[tuple[str, str]]
Searches cryptocurrency names (case-insensitive, substring match). Returns list of (symbol, name) tuples.

**Examples:**
```python
get_symbols_by_name("bitcoin")  # [("BTC-USD", "Bitcoin USD"), ("BCH-USD", "Bitcoin Cash USD"), ...]
get_symbols_by_name("ethereum") # [("ETH-USD", "Ethereum USD"), ("ETC-USD", "Ethereum Classic USD")]
get_symbols_by_name("doge")     # [("DOGE-USD", "Dogecoin USD")]
```

**Use Cases:**
- Convert user-friendly names to symbols
- Handle ambiguous input (multiple matches)
- Discover cryptocurrencies by partial name

## Workflow Patterns

### Pattern 1: Symbol Validation
```python
matches = get_symbols_by_name(user_query)
if not matches:
    return "Cryptocurrency not found"
elif len(matches) == 1:
    symbol, name = matches[0]
    # Use with market API
else:
    # Multiple matches - ask user to clarify
    return f"Multiple matches: {[name for _, name in matches]}"
```

### Pattern 2: Batch Resolution
```python
names = ["Bitcoin", "Ethereum", "UnknownCoin"]
resolved = []
failed = []
for name in names:
    matches = get_symbols_by_name(name.lower())
    if matches:
        resolved.append(matches[0][0])
    else:
        failed.append(name)
# Use resolved with market_tool.get_products(resolved)
```

## Integration with Market Tools
1. User provides name (e.g., "Bitcoin")
2. Search: `get_symbols_by_name("bitcoin")` → `("BTC-USD", "Bitcoin USD")`
3. Fetch price: `market_tool.get_product("BTC-USD")`
4. Return result

## Symbol Format
- Yahoo Finance format: `BTC-USD`, `ETH-USD` (includes `-USD` suffix)
- Some APIs need base only: strip suffix with `symbol.split('-')[0]` → `"BTC"`

## Common Mappings
Bitcoin→BTC-USD | Ethereum→ETH-USD | Solana→SOL-USD | Cardano→ADA-USD | Dogecoin→DOGE-USD

## Critical Rules
1. Always search before using names - never assume direct conversion
2. Handle multiple matches (e.g., "Bitcoin" matches BTC and BCH)
3. Case-insensitive: always use `.lower()` for queries
4. Check empty results before accessing
5. Remember `-USD` suffix in Yahoo symbols

## Search Best Practices
- ✅ Full names: "ethereum", "bitcoin", "solana"
- ✅ Partial OK: "doge" finds "Dogecoin"
- ❌ Avoid: ticker symbols ("BTC"), too generic ("coin")

## Cache Notes
- Cache file: `resources/cryptos.csv` (~1,500+ symbols)
- No API calls during queries (instant response)
- Loaded automatically on initialization
- Static snapshot, not real-time

## Error Handling
- Empty cache → Ensure `resources/cryptos.csv` exists
- No results → Try broader terms, check spelling
- Multiple matches → Show all, ask user to clarify
- Symbol format mismatch → Strip `-USD` suffix if needed
