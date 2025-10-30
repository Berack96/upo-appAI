# Crypto Symbols Tool - Usage Instructions

## OVERVIEW
This toolkit provides access to cryptocurrency symbol lookup and search functionality. It maintains a cached database of cryptocurrency symbols from Yahoo Finance, enabling fast symbol resolution and name-based searches.

## PURPOSE
- **Symbol Lookup**: Get complete list of available cryptocurrency symbols
- **Name Search**: Find cryptocurrency symbols by searching their names
- **Symbol Resolution**: Convert common names to trading symbols for use with market data APIs
- **Cache Management**: Maintains local cache for fast queries without repeated API calls

## AVAILABLE TOOLS (2 total)

### 1. **get_all_symbols()** → list[str]
Returns a complete list of all cryptocurrency symbols available in the cached database.

**Behavior:**
- Returns all symbols from the local cache (CSV file)
- No API calls - instant response
- Returns empty list if cache is not populated

**Returns:**
- `list[str]`: List of cryptocurrency symbols (e.g., ["BTC-USD", "ETH-USD", "SOL-USD", ...])

**Example Usage:**
```python
all_symbols = get_all_symbols()
print(f"Total cryptocurrencies available: {len(all_symbols)}")
# Output: Total cryptocurrencies available: 1523

# Check if specific symbol exists
if "BTC-USD" in all_symbols:
    print("Bitcoin is available")
```

**Use Cases:**
- Verify if a cryptocurrency is supported before fetching data
- Get complete list of available assets for comprehensive analysis
- Validate user input against known symbols
- Browse all available cryptocurrencies

**Important Notes:**
- Symbols include suffix (e.g., "BTC-USD" not just "BTC")
- Cache must be populated first (happens automatically on initialization if cache file exists)
- Returns snapshot from last cache update, not real-time availability

---

### 2. **get_symbols_by_name(query: str)** → list[tuple[str, str]]
Searches for cryptocurrency symbols whose names contain the query string (case-insensitive).

**Arguments:**
- `query` (str): Search term to match against cryptocurrency names

**Returns:**
- `list[tuple[str, str]]`: List of (symbol, name) tuples matching the query
- Returns empty list if no matches found

**Example Usage:**
```python
# Search for Bitcoin-related cryptocurrencies
results = get_symbols_by_name("bitcoin")
# Returns: [("BTC-USD", "Bitcoin USD"), ("BTT-USD", "Bitcoin Token USD"), ...]

# Search for Ethereum
results = get_symbols_by_name("ethereum")
# Returns: [("ETH-USD", "Ethereum USD"), ("ETC-USD", "Ethereum Classic USD"), ...]

# Partial name search
results = get_symbols_by_name("doge")
# Returns: [("DOGE-USD", "Dogecoin USD"), ...]

# Check if found
if results:
    symbol, name = results[0]
    print(f"Found: {name} with symbol {symbol}")
else:
    print("No cryptocurrencies found matching query")
```

**Search Behavior:**
- Case-insensitive matching
- Partial match (substring search)
- Searches only in the "Name" field, not symbols
- Returns all matches, not just the first one

**Use Cases:**
- Convert user-friendly names to trading symbols
- Handle ambiguous user input ("bitcoin" → multiple results including Bitcoin, Bitcoin Cash, etc.)
- Discover cryptocurrencies by partial name
- Validate and suggest corrections for misspelled names

**Best Practices:**
- Use full or near-full names for precise matches
- Handle multiple results - ask user to clarify if ambiguous
- Always check if results list is empty before accessing
- Display both symbol and name to user for confirmation

---

## SYMBOL FORMAT

**Yahoo Finance Symbol Format:**
- All symbols include currency suffix: `-USD`
- Example: `BTC-USD`, `ETH-USD`, `SOL-USD`

**Common Conversions:**
```
User Input    →  Search Query       →  Symbol Result
"Bitcoin"     →  "bitcoin"          →  "BTC-USD"
"Ethereum"    →  "ethereum"         →  "ETH-USD"
"Solana"      →  "solana"           →  "SOL-USD"
"Cardano"     →  "cardano"          →  "ADA-USD"
"Dogecoin"    →  "dogecoin"         →  "DOGE-USD"
```

**When Using Symbols with Market APIs:**
- Some APIs require just the base symbol: `BTC`, `ETH`
- Some APIs require the full Yahoo format: `BTC-USD`
- Check individual market API documentation for required format
- You may need to strip the `-USD` suffix: `symbol.split('-')[0]`

---

## CACHE MANAGEMENT

**Cache File Location:**
- Default: `resources/cryptos.csv`
- Contains: Symbol, Name, and other metadata columns

**Cache Initialization:**
- Cache loaded automatically on tool initialization if file exists
- If cache file doesn't exist, `get_all_symbols()` returns empty list
- Cache can be refreshed using `fetch_crypto_symbols(force_refresh=True)` (admin function)

**Cache Contents:**
- Approximately 1,500+ cryptocurrency symbols
- Includes major coins (BTC, ETH, SOL) and smaller altcoins
- Updated periodically from Yahoo Finance

**Performance:**
- All queries are **instant** - no API calls during normal use
- Cache lookup is O(1) for get_all_symbols
- Search is O(n) for get_symbols_by_name but very fast for ~1,500 entries

---

## WORKFLOW PATTERNS

### **Pattern 1: Symbol Validation**
```python
# User asks for "Bitcoin" price
user_query = "bitcoin"

# Search for matching symbols
matches = get_symbols_by_name(user_query)

if not matches:
    # No matches found
    return "Cryptocurrency not found. Please check the name."
elif len(matches) == 1:
    # Single match - proceed
    symbol, name = matches[0]
    # Use symbol with market API: market_tool.get_product(symbol)
else:
    # Multiple matches - ask user to clarify
    options = "\n".join([f"- {name} ({symbol})" for symbol, name in matches])
    return f"Multiple matches found:\n{options}\nPlease specify which one."
```

### **Pattern 2: Symbol Discovery**
```python
# User asks "What coins are available?"
all_symbols = get_all_symbols()
total_count = len(all_symbols)

# Show sample or summary
top_10 = all_symbols[:10]
return f"There are {total_count} cryptocurrencies available. Top 10: {', '.join(top_10)}"
```

### **Pattern 3: Fuzzy Matching**
```python
# User types "etherium" (misspelled)
query = "etherium"
matches = get_symbols_by_name(query)

if not matches:
    # Try alternative spellings
    alternatives = ["ethereum", "ether"]
    for alt in alternatives:
        matches = get_symbols_by_name(alt)
        if matches:
            return f"Did you mean {matches[0][1]}? (Symbol: {matches[0][0]})"
    return "No matches found"
else:
    # Found matches
    return matches
```

### **Pattern 4: Batch Symbol Resolution**
```python
# User asks for multiple cryptocurrencies
user_requests = ["Bitcoin", "Ethereum", "Solana", "UnknownCoin"]
resolved_symbols = []
failed = []

for name in user_requests:
    matches = get_symbols_by_name(name.lower())
    if matches:
        resolved_symbols.append(matches[0][0])  # Take first match
    else:
        failed.append(name)

# Now use resolved_symbols with market API
if resolved_symbols:
    prices = market_tool.get_products(resolved_symbols)
    
if failed:
    print(f"Warning: Could not find symbols for: {', '.join(failed)}")
```

---

## INTEGRATION WITH MARKET TOOLS

**Typical Workflow:**
1. User provides cryptocurrency name (e.g., "Bitcoin", "Ethereum")
2. Use `get_symbols_by_name()` to find matching symbol
3. Pass symbol to Market Tool APIs (get_product, get_products, etc.)
4. Return price data to user

**Example Integration:**
```python
# Step 1: User request
user_input = "Get Bitcoin price"

# Step 2: Extract cryptocurrency name and search
crypto_name = "bitcoin"  # Extracted from user_input
matches = get_symbols_by_name(crypto_name)

if not matches:
    return "Cryptocurrency not found"

symbol, full_name = matches[0]

# Step 3: Fetch price data
price_data = market_tool.get_product(symbol)

# Step 4: Return result
return f"{full_name} ({symbol}): ${price_data.price}"
```

---

## CRITICAL RULES

1. **Always Search Before Using Names**: Never assume a name directly converts to a symbol
2. **Handle Multiple Matches**: Names like "Bitcoin" might match multiple cryptocurrencies
3. **Case-Insensitive Search**: Always use lowercase for query consistency
4. **Check Empty Results**: Always verify search results before accessing
5. **Symbol Format**: Remember Yahoo symbols have `-USD` suffix
6. **Cache Dependency**: Tools require cache to be populated (usually automatic)

---

## COMMON USE CASES

### **Use Case 1: Name to Symbol Conversion**
User says: "What's the price of Cardano?"
1. Search: `get_symbols_by_name("cardano")`
2. Get symbol: `"ADA-USD"`
3. Fetch price: `market_tool.get_product("ADA-USD")`

### **Use Case 2: Symbol Verification**
User provides: "BTC-USD"
1. Check: `"BTC-USD" in get_all_symbols()`
2. If True, proceed with API call
3. If False, suggest similar names

### **Use Case 3: Discovery**
User asks: "What cryptos start with 'Sol'?"
1. Search: `get_symbols_by_name("sol")`
2. Return all matches (Solana, etc.)

### **Use Case 4: Ambiguity Resolution**
User says: "Bitcoin"
1. Search: `get_symbols_by_name("bitcoin")`
2. Results: `[("BTC-USD", "Bitcoin USD"), ("BCH-USD", "Bitcoin Cash USD"), ...]`
3. Ask user: "Did you mean Bitcoin (BTC) or Bitcoin Cash (BCH)?"

---

## ERROR HANDLING

**Common Issues:**

1. **Empty Cache**
   - Symptom: `get_all_symbols()` returns empty list
   - Cause: Cache file missing or not loaded
   - Solution: Ensure `resources/cryptos.csv` exists

2. **No Search Results**
   - Symptom: `get_symbols_by_name()` returns empty list
   - Cause: Query doesn't match any cryptocurrency names
   - Solution: Try broader search terms, check spelling, suggest alternatives

3. **Multiple Matches**
   - Symptom: Search returns many results
   - Cause: Query is too broad (e.g., "coin")
   - Solution: Ask user to be more specific, show all matches

4. **Symbol Format Mismatch**
   - Symptom: Market API fails with Yahoo symbol
   - Cause: API expects different format
   - Solution: Strip suffix: `symbol.split('-')[0]` → `"BTC-USD"` becomes `"BTC"`

---

## SEARCH TIPS

**Effective Searches:**
- ✅ Use full names: "ethereum", "bitcoin", "solana"
- ✅ Use common names: "ether" finds "Ethereum"
- ✅ Partial names work: "doge" finds "Dogecoin"

**Ineffective Searches:**
- ❌ Ticker symbols: "BTC" (search by name, not symbol)
- ❌ Too generic: "coin", "token" (returns too many results)
- ❌ Abbreviations: "eth" might not match "Ethereum" (try full name)

**Best Practice:**
If user provides a ticker symbol (BTC, ETH), first check if it exists in `get_all_symbols()`, then try name search as fallback.

---

## PERFORMANCE NOTES

- **get_all_symbols()**: O(1) - Instant
- **get_symbols_by_name()**: O(n) - Fast (< 1ms for ~1,500 entries)
- **No Network Calls**: All data served from local cache
- **Memory Efficient**: CSV loaded once on initialization

---

## LIMITATIONS

1. **Yahoo Finance Dependency**: Symbol list limited to what Yahoo Finance provides
2. **No Real-Time Updates**: Cache is static snapshot, not live data
3. **Name Matching Only**: Cannot search by symbol, market cap, or other criteria
4. **USD Pairs Only**: Only symbols with `-USD` suffix are included
5. **No Metadata**: Only symbol and name available, no price, volume, or market cap in this tool
