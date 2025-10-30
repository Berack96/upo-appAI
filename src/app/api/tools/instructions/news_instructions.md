News APIs Toolkit - Usage Instructions

OVERVIEW:
This toolkit provides access to cryptocurrency and general news articles from multiple providers (NewsAPI, Google News, CryptoPanic, DuckDuckGo). You can query a single provider for fast results or aggregate data from all providers for comprehensive coverage.

AVAILABLE TOOLS (4 total):

=== SINGLE-SOURCE TOOLS (FAST) ===
These tools query providers sequentially and return data from the first one that responds successfully.

1. get_top_headlines(limit: int = 100) → list[Article]
   - Fetches top cryptocurrency headlines from the first available provider
   - Example: get_top_headlines(limit=10)
   - Use when: User wants a quick overview of current crypto news
   - Returns: List of Article objects with title, source, url, published date

2. get_latest_news(query: str, limit: int = 100) → list[Article]
   - Searches for news articles on a specific topic
   - Example: get_latest_news("Bitcoin ETF", limit=20)
   - Use when: User wants news about a specific topic or event
   - Returns: List of Article objects matching the search query

=== AGGREGATED TOOLS (COMPREHENSIVE) ===
These tools query ALL configured providers and return results from each source for maximum coverage.

3. get_top_headlines_aggregated(limit: int = 100) → dict[str, list[Article]]
   - Queries ALL providers for top headlines
   - Returns dictionary mapping provider names to their article lists
   - Example: get_top_headlines_aggregated(limit=15)
   - Use when: User requests "comprehensive", "all sources", or "complete" news coverage
   - Warning: Uses 4x API calls (one per provider)

4. get_latest_news_aggregated(query: str, limit: int = 100) → dict[str, list[Article]]
   - Queries ALL providers for news on a specific topic
   - Returns dictionary mapping provider names to their article lists
   - Example: get_latest_news_aggregated("Ethereum merge", limit=20)
   - Use when: User requests detailed research or comprehensive topic coverage
   - Warning: Uses 4x API calls

TOOL SELECTION STRATEGY:
- "What's the latest crypto news?" → get_top_headlines(limit=10) [tool #1]
- "Find news about Bitcoin" → get_latest_news("Bitcoin", limit=20) [tool #2]
- "Get all sources for crypto news" → get_top_headlines_aggregated(limit=10) [tool #3]
- "Research Ethereum from all sources" → get_latest_news_aggregated("Ethereum", limit=15) [tool #4]

QUERY FORMULATION:
When users ask about specific topics, construct clear search queries:
- "Bitcoin regulation" → query="Bitcoin regulation"
- "ETH price surge" → query="Ethereum price increase"
- "Crypto market crash" → query="cryptocurrency market crash"
- "NFT trends" → query="NFT trends"
- "DeFi security" → query="DeFi security vulnerabilities"

ARTICLE STRUCTURE:
Each Article object typically contains:
- title: Article headline
- source: Publication/website name
- url: Link to full article
- published_at: Publication timestamp
- description: Article summary (when available)
- author: Article author (when available)

LIMIT GUIDELINES:
- Quick overview: limit=5-10
- Standard news scan: limit=20-30
- Deep research: limit=50-100
- Each provider respects the limit independently in aggregated mode

CRITICAL RULES:
1. NEVER fabricate news articles or headlines - only report actual tool outputs
2. ALL articles returned by tools are REAL and from actual news sources
3. ALWAYS include article source and publication date when available
4. ALWAYS include article URLs so users can verify information
5. If tools fail, report the failure explicitly - DO NOT invent placeholder articles
6. In aggregated results, clearly separate articles by provider

ERROR HANDLING:
- All providers fail → Report "News data unavailable from all sources"
- Partial data → Report available articles and note which sources failed
- No results for query → Report "No news articles found for '[QUERY]'. Try broader terms"
- API rate limits → Try single-source tools instead of aggregated tools

OUTPUT REQUIREMENTS:
- Include article title (required)
- Include source/publication name (required)
- Include URL for verification (required)
- Include publication date/time when available
- Provide brief summary/description when available
- Group articles by source in aggregated mode
- Be concise to save tokens - focus on headlines and key info
- Deduplicate articles when same story appears from multiple sources

SEARCH BEST PRACTICES:
- Use specific keywords for focused results
- Use broader terms if no results found
- Include cryptocurrency names in full (Bitcoin not just BTC)
- Consider alternative spellings or synonyms
- Avoid overly technical jargon in queries
