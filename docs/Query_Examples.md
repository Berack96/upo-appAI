# Query Examples - Cryptocurrency Report Generation

This document provides examples of user queries that trigger specific tools in the cryptocurrency analysis application.

## Table of Contents
- [CryptoSymbolsTools - Symbol Resolution](#1-cryptosymbolstools---symbol-resolution)
- [MarketAPIsTool - Price & Historical Data](#2-marketapistool---price--historical-data)
- [NewsAPIsTool - News & Sentiment](#3-newsapistool---news--sentiment)
- [SocialAPIsTool - Social Media Sentiment](#4-socialapistool---social-media-sentiment)
- [PlanMemoryTool - Task Management](#5-planmemorytool---task-management)
- [ReasoningTools - Cognitive Analysis](#6-reasoningtools---cognitive-analysis)
- [Composite Queries - Multiple Tools](#7-composite-queries---multiple-tools)
- [Keyword Triggers Reference](#keyword-triggers---quick-reference)

---

## 1. CryptoSymbolsTools - Symbol Resolution

### `get_symbols_by_name(query)` - Resolve cryptocurrency names to symbols

**Purpose:** Convert user-friendly names to trading symbols before calling market APIs.

**Example Queries:**
- ❓ "Dammi il prezzo di **Ethereum**" 
  - → Searches "ethereum" → Finds "ETH-USD"
  
- ❓ "Analizza **Solana** e **Cardano**"
  - → Resolves both names to SOL-USD, ADA-USD
  
- ❓ "Quanto vale **Dogecoin**?"
  - → Searches "dogecoin" → Finds "DOGE-USD"
  
- ❓ "Confronta **Bitcoin** e **Bitcoin Cash**"
  - → Handles ambiguity (2 matches: BTC-USD, BCH-USD)
  
- ❓ "Report su **Polkadot**"
  - → Resolves to "DOT-USD"

**Trigger Words:** Cryptocurrency common names (Bitcoin, Ethereum, Solana, etc.)

---

### `get_all_symbols()` - List all available cryptocurrencies

**Purpose:** Verify symbol availability or show complete list.

**Example Queries:**
- ❓ "Quali criptovalute sono disponibili?"
- ❓ "Mostrami tutte le crypto supportate"
- ❓ "Lista completa delle criptovalute"
- ❓ "Esiste **XYZ-USD** nel sistema?"
  - → Verifies if symbol exists in list

**Trigger Words:** "disponibili", "supportate", "lista", "tutte", "esiste"

---

## 2. MarketAPIsTool - Price & Historical Data

### Single-Source Tools (FAST - First available provider)

#### `get_product(asset_id)` - Current price for single asset

**Purpose:** Quick price check for one cryptocurrency.

**Example Queries:**
- ❓ "Qual è il prezzo attuale di Bitcoin?"
- ❓ "Quanto vale BTC adesso?"
- ❓ "Prezzo corrente di Ethereum"
- ❓ "Valore di SOL?"
- ❓ "Quotazione Cardano"

**Trigger Words:** "prezzo", "quanto vale", "valore", "quotazione", "attuale", "corrente", "adesso"

---

#### `get_products(asset_ids)` - Current prices for multiple assets

**Purpose:** Quick price comparison of multiple cryptocurrencies.

**Example Queries:**
- ❓ "Dammi i prezzi di BTC, ETH e SOL"
- ❓ "Confronta i valori di Bitcoin, Ethereum e Cardano"
- ❓ "Lista prezzi: BTC, DOGE, ADA"
- ❓ "Prezzi attuali delle top 5 crypto"
- ❓ "Quanto valgono Bitcoin ed Ethereum?"

**Trigger Words:** Multiple assets mentioned, "confronta", "lista prezzi", "valori di"

---

#### `get_historical_prices(asset_id, limit)` - Historical data for single asset

**Purpose:** Price history and trend analysis.

**Example Queries:**
- ❓ "Prezzo di Bitcoin negli ultimi 7 giorni"
- ❓ "Storico di ETH dell'ultimo mese"
- ❓ "Come è variato Solana nelle ultime 24 ore?"
- ❓ "Andamento BTC ultima settimana"
- ❓ "Grafico storico di Ethereum"

**Trigger Words:** "storico", "ultimi N giorni/ore", "ultimo mese", "variato", "andamento", "trend", "grafico"

**Time Range Mapping:**
- "ultime 24 ore" / "oggi" → limit=24 (hourly) or limit=1 (daily)
- "ultimi 7 giorni" / "ultima settimana" → limit=7
- "ultimo mese" / "ultimi 30 giorni" → limit=30
- "ultimi 3 mesi" → limit=90

---

### Aggregated Tools (COMPREHENSIVE - All providers with VWAP)

#### `get_product_aggregated(asset_id)` - Accurate price from all sources

**Purpose:** Most reliable price using Volume Weighted Average Price (VWAP) from all providers.

**Example Queries:**
- ❓ "Dammi il prezzo **più accurato** di Bitcoin"
- ❓ "Qual è il prezzo **affidabile** di ETH?"
- ❓ "Voglio il prezzo di BTC da **tutte le fonti**"
- ❓ "Prezzo **preciso** di Solana"
- ❓ "Prezzo **verificato** di Cardano"

**Trigger Words:** "accurato", "affidabile", "preciso", "verificato", "tutte le fonti", "completo", "da tutti i provider"

---

#### `get_products_aggregated(asset_ids)` - Accurate prices for multiple assets

**Purpose:** Comprehensive multi-asset analysis with aggregated data.

**Example Queries:**
- ❓ "Analisi **dettagliata** dei prezzi di BTC ed ETH"
- ❓ "Confronto **completo** tra Bitcoin e Ethereum"
- ❓ "Report **comprensivo** su BTC, ETH, SOL"
- ❓ "Dati **affidabili** per top 3 crypto"
- ❓ "Prezzi **aggregati** di Bitcoin e Cardano"

**Trigger Words:** "dettagliata", "completo", "comprensivo", "affidabili", "aggregati" + multiple assets

---

#### `get_historical_prices_aggregated(asset_id, limit)` - Historical data from all sources

**Purpose:** Complete historical analysis with data from all providers.

**Example Queries:**
- ❓ "Storico **completo** di Bitcoin da tutte le fonti"
- ❓ "Analisi **comprensiva** del prezzo di ETH nell'ultimo mese"
- ❓ "Dati storici **affidabili** di BTC"
- ❓ "Andamento **dettagliato** di Solana ultimi 7 giorni"
- ❓ "Trend **aggregato** di Cardano"

**Trigger Words:** "storico completo", "comprensiva", "affidabili", "dettagliato", "aggregato" + time range

---

## 3. NewsAPIsTool - News & Sentiment

### Single-Source Tools (FAST - First available provider)

#### `get_top_headlines(limit)` - Top cryptocurrency news

**Purpose:** Quick overview of current crypto news headlines.

**Example Queries:**
- ❓ "Quali sono le ultime notizie crypto?"
- ❓ "Dammi i titoli principali sulle criptovalute"
- ❓ "Cosa dicono le news oggi?"
- ❓ "Notizie del giorno crypto"
- ❓ "Ultime breaking news Bitcoin"

**Trigger Words:** "notizie", "news", "titoli", "ultime", "del giorno", "breaking"

**Limit Guidelines:**
- Quick scan: limit=5-10
- Standard: limit=20-30
- Deep research: limit=50-100

---

#### `get_latest_news(query, limit)` - News on specific topic

**Purpose:** Search for news articles about specific crypto topics or events.

**Example Queries:**
- ❓ "Notizie su **Bitcoin ETF**"
- ❓ "Cosa si dice del **crollo di Ethereum**?"
- ❓ "Trova articoli sulla **regolamentazione crypto**"
- ❓ "News su **DeFi security**"
- ❓ "Articoli su **NFT trends**"
- ❓ "Cosa dicono delle **whale movements**?"

**Trigger Words:** "notizie su", "articoli su", "cosa si dice", "trova", "cerca" + specific topic

**Query Formulation Tips:**
- User: "Bitcoin regulation" → query="Bitcoin regulation"
- User: "ETH price surge" → query="Ethereum price increase"
- User: "Crypto market crash" → query="cryptocurrency market crash"

---

### Aggregated Tools (COMPREHENSIVE - All news providers)

#### `get_top_headlines_aggregated(limit)` - Headlines from all sources

**Purpose:** Complete news coverage from all configured providers (NewsAPI, Google News, CryptoPanic, DuckDuckGo).

**Example Queries:**
- ❓ "Dammi le notizie crypto da **tutte le fonti**"
- ❓ "Panoramica **completa** delle news di oggi"
- ❓ "Cosa dicono **tutti i provider** sulle crypto?"
- ❓ "Confronta le notizie da **diverse fonti**"
- ❓ "Headline **aggregate** crypto"

**Trigger Words:** "tutte le fonti", "completa", "tutti i provider", "diverse fonti", "aggregate", "panoramica"

---

#### `get_latest_news_aggregated(query, limit)` - Topic news from all sources

**Purpose:** Comprehensive research on specific topic from all news providers.

**Example Queries:**
- ❓ "Ricerca **approfondita** su Bitcoin regulation"
- ❓ "Analisi **completa** delle notizie su Ethereum merge"
- ❓ "**Tutte le fonti** su NFT trends"
- ❓ "Confronto notizie da **tutti i provider** su DeFi"
- ❓ "Report **comprensivo** news Bitcoin ETF"

**Trigger Words:** "approfondita", "completa", "tutte le fonti", "tutti i provider", "comprensivo", "ricerca"

---

## 4. SocialAPIsTool - Social Media Sentiment

### Single-Source Tool (FAST - First available platform)

#### `get_top_crypto_posts(limit)` - Top social media posts

**Purpose:** Quick snapshot of social media sentiment on crypto.

**Example Queries:**
- ❓ "Cosa dice la gente sulle crypto?"
- ❓ "Sentiment sui social media per Bitcoin"
- ❓ "Discussioni trending su Reddit/Twitter"
- ❓ "Qual è il mood della community?"
- ❓ "Post popolari su crypto oggi"
- ❓ "Cosa dicono gli utenti di Ethereum?"

**Trigger Words:** "cosa dice", "sentiment", "discussioni", "mood", "community", "social", "Reddit", "Twitter"

**Limit Guidelines:**
- Quick snapshot: limit=5 (default, posts are long)
- Standard: limit=10-15
- Deep analysis: limit=20-30

---

### Aggregated Tool (COMPREHENSIVE - All platforms)

#### `get_top_crypto_posts_aggregated(limit_per_wrapper)` - Posts from all platforms

**Purpose:** Complete social sentiment analysis across Reddit, X/Twitter, and 4chan.

**Example Queries:**
- ❓ "Sentiment su **tutte le piattaforme** social"
- ❓ "Confronta Reddit e Twitter su Bitcoin"
- ❓ "Analisi **completa** delle discussioni social"
- ❓ "Cosa dicono **tutti** (Reddit, Twitter, 4chan)?"
- ❓ "Panoramica **social aggregate** su crypto"
- ❓ "Mood su **tutte le piattaforme** crypto"

**Trigger Words:** "tutte le piattaforme", "confronta", "completa", "tutti", "aggregate", "panoramica"

---

## 5. PlanMemoryTool - Task Management

**Note:** This tool is used **internally** by the Team Leader agent. Users don't call it directly, but complex queries trigger automatic task planning.

### Automatic Triggering by Query Complexity

#### Simple Query (1-2 tasks):
- ❓ "Prezzo di Bitcoin"
  - → Creates 1 task: "Fetch BTC price"

- ❓ "Notizie su Ethereum"
  - → Creates 1 task: "Get Ethereum news"

#### Complex Query (3+ tasks):
- ❓ "**Report completo** su Bitcoin"
  - → Creates 3 tasks:
    1. "Fetch BTC-USD current price and historical data"
    2. "Analyze Bitcoin news sentiment (last 24h, limit=20)"
    3. "Check Bitcoin social discussions (limit=10)"

- ❓ "Analizza il mercato crypto oggi"
  - → Creates multiple tasks:
    1. "Get top crypto prices (BTC, ETH, SOL, ADA)"
    2. "Get crypto news headlines (limit=30)"
    3. "Check social sentiment on crypto market"

**Trigger Words for Complex Queries:** "report completo", "analisi completa", "analizza", "studio", "ricerca approfondita"

---

## 6. ReasoningTools - Cognitive Analysis

**Note:** This tool is used **internally** by the Team Leader for decision-making. Triggered automatically during complex operations.

### `think()` - Step-by-step reasoning

**Automatic Triggers:**
- **Ambiguous Query:** "Bitcoin" → think: "Could be BTC or BCH, need to verify with CryptoSymbolsTools"
- **Strategy Decision:** Query with "accurate" → think: "User wants reliable data, should use aggregated tools"
- **Retry Strategy:** API failed → think: "Timeout error, should retry with broader parameters"

### `analyze()` - Result evaluation

**Automatic Triggers:**
- **After MarketAgent response:** → analyze: "Fresh data, high volume, proceed to next task"
- **After API failure:** → analyze: "API timeout, retry with modified parameters"
- **Before final report:** → analyze: "All 3 data sources complete, data quality high, generate comprehensive report"

---

## 7. Composite Queries - Multiple Tools

### Full Analysis Queries (Trigger ALL tools)

#### Query: **"Report completo su Bitcoin"**

**Tools Triggered:**
1. **CryptoSymbolsTools**: `get_symbols_by_name("bitcoin")` → "BTC-USD"
2. **MarketAPIsTool**: `get_products_aggregated(["BTC-USD"])`
3. **NewsAPIsTool**: `get_latest_news_aggregated("Bitcoin", limit=20)`
4. **SocialAPIsTool**: `get_top_crypto_posts_aggregated(limit=10)`
5. **PlanMemoryTool**: Creates 3 tasks, tracks execution, stores results
6. **ReasoningTools**: Think/analyze for each decision and synthesis

**Expected Output:** Comprehensive report with price data, sentiment analysis, social trends, and metadata.

---

#### Query: **"Confronta Bitcoin ed Ethereum: prezzi, news e sentiment"**

**Tools Triggered:**
1. **CryptoSymbolsTools**: 
   - `get_symbols_by_name("bitcoin")` → BTC-USD
   - `get_symbols_by_name("ethereum")` → ETH-USD
2. **MarketAPIsTool**: `get_products(["BTC-USD", "ETH-USD"])`
3. **NewsAPIsTool**: 
   - `get_latest_news("Bitcoin", limit=20)`
   - `get_latest_news("Ethereum", limit=20)`
4. **SocialAPIsTool**: `get_top_crypto_posts(limit=20)` → filter for BTC/ETH mentions
5. **PlanMemoryTool**: Creates 6 tasks (2 assets × 3 data types)
6. **ReasoningTools**: Compare and synthesize findings between BTC and ETH

**Expected Output:** Side-by-side comparison report with price differences, sentiment comparison, and cross-analysis.

---

#### Query: **"Come è cambiato Bitcoin nell'ultima settimana? Analizza prezzo, news e social"**

**Tools Triggered:**
1. **CryptoSymbolsTools**: `get_symbols_by_name("bitcoin")` → BTC-USD
2. **MarketAPIsTool**: `get_historical_prices("BTC-USD", limit=7)`
3. **NewsAPIsTool**: `get_latest_news("Bitcoin", limit=30)` → filter last 7 days
4. **SocialAPIsTool**: `get_top_crypto_posts(limit=20)` → filter last 7 days
5. **PlanMemoryTool**: Creates tasks for fetch + trend analysis
6. **ReasoningTools**: Analyze correlation between price changes and sentiment trends

**Expected Output:** Temporal analysis report showing price evolution, news sentiment over time, and social mood changes.

---

### Multi-Asset Analysis

#### Query: **"Report sui prezzi delle top 5 crypto con analisi di mercato"**

**Tools Triggered:**
1. **CryptoSymbolsTools**: Resolve top 5 crypto names to symbols
2. **MarketAPIsTool**: `get_products_aggregated(["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "DOT-USD"])`
3. **NewsAPIsTool**: `get_top_headlines(limit=50)` → extract relevant news for each
4. **SocialAPIsTool**: `get_top_crypto_posts_aggregated(limit=15)` → categorize by asset
5. **PlanMemoryTool**: Manages multi-asset task orchestration
6. **ReasoningTools**: Cross-asset comparison and market overview synthesis

---

### Focused Deep Dive

#### Query: **"Ricerca approfondita su Ethereum: storico 30 giorni, tutte le news, sentiment social completo"**

**Tools Triggered:**
1. **CryptoSymbolsTools**: `get_symbols_by_name("ethereum")` → ETH-USD
2. **MarketAPIsTool**: `get_historical_prices_aggregated("ETH-USD", limit=30)`
3. **NewsAPIsTool**: `get_latest_news_aggregated("Ethereum", limit=100)`
4. **SocialAPIsTool**: `get_top_crypto_posts_aggregated(limit_per_wrapper=30)`
5. **PlanMemoryTool**: Sequential execution with data validation
6. **ReasoningTools**: In-depth analysis with trend identification

**Expected Output:** Extensive Ethereum report with 30-day price chart, comprehensive news analysis, and detailed social sentiment breakdown.

---

## Keyword Triggers - Quick Reference

| Keyword / Phrase | Tool / Function | Type |
|------------------|-----------------|------|
| **Price-related** |
| "prezzo", "quanto vale", "valore", "quotazione" | `get_product()` | Market - Single |
| "prezzi di [list]", "confronta prezzi" | `get_products()` | Market - Single |
| "accurato", "affidabile", "tutte le fonti", "preciso" | `get_product_aggregated()` | Market - Aggregated |
| "storico", "ultimi N giorni", "variazione", "trend" | `get_historical_prices()` | Market - Historical |
| "storico completo", "dati aggregati storici" | `get_historical_prices_aggregated()` | Market - Historical Agg |
| **News-related** |
| "notizie", "news", "articoli", "titoli" | `get_top_headlines()` | News - Single |
| "notizie su [topic]", "articoli su [topic]" | `get_latest_news()` | News - Single |
| "tutte le fonti news", "panoramica completa news" | `get_top_headlines_aggregated()` | News - Aggregated |
| "ricerca approfondita", "tutti i provider" | `get_latest_news_aggregated()` | News - Aggregated |
| **Social-related** |
| "sentiment", "cosa dice la gente", "mood", "community" | `get_top_crypto_posts()` | Social - Single |
| "tutte le piattaforme", "Reddit e Twitter", "social completo" | `get_top_crypto_posts_aggregated()` | Social - Aggregated |
| **Comprehensive** |
| "report completo", "analisi completa" | ALL tools | Comprehensive |
| "ricerca approfondita", "studio dettagliato" | ALL tools | Comprehensive |
| "confronta [A] e [B]", "differenza tra" | Multiple assets | Comparison |
| **Symbol Resolution** |
| "Bitcoin", "Ethereum", "Solana" (names not symbols) | `get_symbols_by_name()` | Symbol Lookup |
| "disponibili", "lista crypto", "supportate" | `get_all_symbols()` | Symbol List |

---

## Best Practices for Query Formulation

### For Users:

1. **Be Specific About Scope:**
   - ✅ "Prezzo accurato di Bitcoin da tutte le fonti"
   - ❌ "Bitcoin" (ambiguous)

2. **Use Time Ranges When Relevant:**
   - ✅ "Storico di Ethereum ultimi 30 giorni"
   - ❌ "Storico Ethereum" (unclear timeframe)

3. **Specify Data Completeness Needs:**
   - ✅ "Report completo su Solana con news e social"
   - ❌ "Info su Solana" (unclear what data needed)

4. **Use Common Cryptocurrency Names:**
   - ✅ "Analisi Bitcoin ed Ethereum"
   - ✅ "Confronta BTC e ETH" (both work)

### For Team Leader Agent:

1. **Always Use CryptoSymbolsTools First:**
   - When user mentions names, resolve to symbols before market calls

2. **Choose Single vs Aggregated Based on Keywords:**
   - "accurato", "affidabile", "completo" → Use aggregated
   - Quick queries without qualifiers → Use single-source

3. **Create Descriptive Tasks:**
   - ✅ "Fetch BTC-USD price from Binance (aggregated, VWAP)"
   - ❌ "Get price" (too vague)

4. **Use ReasoningTools Before Decisions:**
   - Before choosing tool variant
   - Before retry strategies
   - Before final synthesis

---

## Time Range Reference

| User Expression | Limit Parameter | Time Period |
|----------------|-----------------|-------------|
| "oggi", "ultime 24 ore" | limit=1 or 24 | 1 day |
| "ultimi 7 giorni", "ultima settimana" | limit=7 | 7 days |
| "ultimo mese", "ultimi 30 giorni" | limit=30 | 30 days |
| "ultimi 3 mesi" | limit=90 | 90 days |
| "ultimi 6 mesi" | limit=180 | 180 days |

---

## Common Query Patterns

### Pattern 1: Quick Price Check
**Query:** "Prezzo di Bitcoin"  
**Flow:** CryptoSymbolsTools → MarketAPIsTool (single) → Result

### Pattern 2: Detailed Analysis
**Query:** "Analisi completa Bitcoin"  
**Flow:** CryptoSymbolsTools → All tools (aggregated) → Synthesis → Comprehensive Report

### Pattern 3: Comparison
**Query:** "Confronta Bitcoin ed Ethereum"  
**Flow:** CryptoSymbolsTools (both) → MarketAPIsTool (both) → NewsAPIsTool (both) → Comparison Report

### Pattern 4: Temporal Trend
**Query:** "Come è cambiato Ethereum nell'ultima settimana"  
**Flow:** CryptoSymbolsTools → Historical Market Data → Recent News → Recent Social → Trend Analysis

### Pattern 5: Multi-Asset Overview
**Query:** "Prezzi delle top 5 crypto"  
**Flow:** CryptoSymbolsTools (×5) → MarketAPIsTool (batch) → Price List Report

---

## Error Handling Examples

### Ambiguous Symbol
**Query:** "Prezzo di Bitcoin"  
**Issue:** Multiple matches (BTC, BCH)  
**Resolution:** ReasoningTools.think() → Ask user or default to BTC-USD

### No Results
**Query:** "Notizie su XYZ crypto"  
**Issue:** No news found  
**Response:** "No news articles found for XYZ. Try broader search terms."

### API Failure
**Query:** "Report completo Bitcoin"  
**Issue:** MarketAPI timeout  
**Resolution:** PlanMemoryTool marks task failed → ReasoningTools decides retry → Retry with broader params

### Partial Data
**Query:** "Analisi completa Ethereum"  
**Issue:** SocialAPI failed, Market and News succeeded  
**Response:** Report with Market and News sections, omit Social section, note in metadata

---

This document serves as a comprehensive reference for understanding how different user queries trigger specific tools in the cryptocurrency analysis application.
