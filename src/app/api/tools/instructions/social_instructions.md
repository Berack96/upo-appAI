Social Media Toolkit - Usage Instructions

OVERVIEW:
This toolkit provides access to cryptocurrency-related social media posts from multiple platforms (Reddit, X/Twitter, 4chan). You can query a single platform for fast results or aggregate data from all platforms for comprehensive social sentiment analysis.

AVAILABLE TOOLS (2 total):

=== SINGLE-SOURCE TOOLS (FAST) ===
These tools query platforms sequentially and return data from the first one that responds successfully.

1. get_top_crypto_posts(limit: int = 5) → list[SocialPost]
   - Fetches top cryptocurrency-related posts from the first available platform
   - Example: get_top_crypto_posts(limit=10)
   - Use when: User wants a quick snapshot of social media sentiment
   - Returns: List of SocialPost objects with content, author, engagement metrics
   - Default limit is intentionally small (5) due to post length

=== AGGREGATED TOOLS (COMPREHENSIVE) ===
These tools query ALL configured platforms and return results from each source for complete social coverage.

2. get_top_crypto_posts_aggregated(limit_per_wrapper: int = 5) → dict[str, list[SocialPost]]
   - Queries ALL platforms for top crypto posts
   - Returns dictionary mapping platform names to their post lists
   - Example: get_top_crypto_posts_aggregated(limit_per_wrapper=10)
   - Use when: User requests "all platforms", "comprehensive", or "complete" social analysis
   - Warning: Uses 3x API calls (one per platform: Reddit, X, 4chan)

TOOL SELECTION STRATEGY:
- "What's trending in crypto on social media?" → get_top_crypto_posts(limit=10) [tool #1]
- "Show top crypto posts" → get_top_crypto_posts(limit=5) [tool #1]
- "Get crypto sentiment from all platforms" → get_top_crypto_posts_aggregated(limit_per_wrapper=10) [tool #2]
- "Compare Reddit and Twitter crypto posts" → get_top_crypto_posts_aggregated(limit_per_wrapper=15) [tool #2]

SOCIALPOST STRUCTURE:
Each SocialPost object typically contains:
- content: Post text/message
- author: Username/handle of poster
- platform: Source platform (Reddit, X, 4chan)
- url: Link to original post
- created_at: Post timestamp
- score/upvotes: Engagement metric (platform-dependent)
- comments_count: Number of comments/replies
- subreddit/board: Specific community (Reddit/4chan)

LIMIT GUIDELINES:
Social media posts are longer than news headlines, so use smaller limits:
- Quick snapshot: limit=5 (default)
- Standard overview: limit=10-15
- Deep analysis: limit=20-30
- Maximum recommended: limit=50 (to avoid token overflow)

PLATFORM-SPECIFIC NOTES:
- Reddit: Posts from r/cryptocurrency, r/bitcoin, r/ethereum and similar subreddits
- X (Twitter): Crypto-related tweets with high engagement
- 4chan: Posts from /biz/ board focused on crypto discussions
- Each platform has different engagement metrics (upvotes, likes, replies)

CRITICAL RULES:
1. NEVER fabricate social media posts - only report actual tool outputs
2. ALL posts returned by tools are REAL from actual users
3. ALWAYS include platform source and author information
4. ALWAYS include post URLs for verification
5. Be aware of potential misinformation in social media content
6. If tools fail, report the failure explicitly - DO NOT invent placeholder posts
7. In aggregated results, clearly separate posts by platform
8. Social media reflects opinions, not facts - frame accordingly

ERROR HANDLING:
- All platforms fail → Report "Social media data unavailable from all sources"
- Partial data → Report available posts and note which platforms failed
- No crypto posts found → Report "No cryptocurrency posts available at this time"
- API rate limits → Try single-source tool or reduce limit

OUTPUT REQUIREMENTS:
- Include post content (truncate if too long, max 280 chars recommended)
- Include author/username (required)
- Include platform name (required)
- Include engagement metrics (upvotes, likes, comments)
- Include post URL for verification
- Include timestamp/date when available
- Group posts by platform in aggregated mode
- Summarize sentiment trends rather than listing all posts verbatim
- Be VERY concise to save tokens - social posts are verbose

SENTIMENT ANALYSIS TIPS:
- Look for recurring topics across posts
- Note positive vs negative sentiment patterns
- Identify trending coins or topics
- Compare sentiment across platforms
- Highlight posts with high engagement
- Flag potential FUD (Fear, Uncertainty, Doubt) or shilling

CONTENT WARNINGS:
- Social media may contain:
  - Unverified information
  - Speculation and rumors
  - Promotional/shilling content
  - Strong opinions or biased views
  - Inappropriate language (especially 4chan)
- Always present social data with appropriate disclaimers
- Do not treat social media posts as factual evidence
- Encourage users to verify information from official sources

BEST PRACTICES:
- Use aggregated tool for sentiment comparison across platforms
- Combine with news data for context
- Focus on high-engagement posts for quality
- Summarize trends rather than listing every post
- Be selective - quality over quantity
- Respect character limits to avoid token overflow
