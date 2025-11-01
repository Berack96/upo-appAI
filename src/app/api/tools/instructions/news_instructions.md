# News APIs - Instructions

## Tools (4)
**Single-source (fast):** First available provider
1. `get_top_headlines(limit=100)` - Top crypto headlines
2. `get_latest_news(query, limit=100)` - Search specific topic

**Aggregated (comprehensive):** All providers (4x API calls)
3. `get_top_headlines_aggregated(limit=100)` - Headlines from all sources
4. `get_latest_news_aggregated(query, limit=100)` - Topic search, all sources

## Selection Strategy
- Quick overview → single-source (tools 1-2)
- Keywords "comprehensive", "all sources", "complete" → aggregated (tools 3-4)

## Query Formulation
- "Bitcoin regulation" → query="Bitcoin regulation"
- "ETH price surge" → query="Ethereum price increase"
- Use full crypto names (Bitcoin not BTC), specific keywords for focus

## Article Structure
Contains: title, source, url, published_at, description (optional), author (optional)

## Limits
- Quick: 5-10 | Standard: 20-30 | Deep: 50-100

## Critical Rules
- Never fabricate articles - only report actual tool outputs
- Always include: title, source, URL, publication date
- Failure handling: Report explicit error, suggest broader terms
- Deduplicate same stories across sources
- Be concise to save tokens
