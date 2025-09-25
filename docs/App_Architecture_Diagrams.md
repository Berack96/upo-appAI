# 📊 Architettura e Flussi dell'App upo-appAI

## 🏗️ Diagramma Architettura Generale

```
┌─────────────────────────────────────────────────────────────────┐
│                        🌐 GRADIO UI                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   User Input    │  │    Provider     │  │     Style       │  │
│  │   (Query)       │  │   (Model)       │  │  (Conservative/ │  │
│  │                 │  │                 │  │   Aggressive)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🔧 TOOL AGENT                                │
│                  (Central Orchestrator)                        │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ 1. Collect Data │  │ 2. Analyze      │  │ 3. Predict &    │ │
│  │                 │  │   Sentiment     │  │   Recommend     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   📊 AGENT ECOSYSTEM                           │
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ ┌───────────┐│
│ │   MARKET    │  │    NEWS     │  │   SOCIAL    │ │ PREDICTOR ││
│ │   AGENT     │  │   AGENT     │  │   AGENT     │ │  AGENT    ││
│ │             │  │             │  │             │ │           ││
│ │ 📈 Coinbase │  │ 📰 News API │  │ 🐦 Social  │ │ 🤖 LLM    ││
│ │ 📊 CryptoCmp│  │             │  │    Media    │ │  Analysis ││
│ │ 🟡 Binance  │  │             │  │             │ │           ││
│ └─────────────┘  └─────────────┘  └─────────────┘ └───────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flusso di Esecuzione Dettagliato

```
👤 USER REQUEST
    │
    │ "Analizza Bitcoin con strategia aggressiva"
    ▼
┌─────────────────────────────────────────────────────────────┐
│                🔧 TOOL AGENT                               │
│                                                             │
│  def interact(query, provider, style):                     │
│      │                                                     │
│      ├── 📊 market_data = market_agent.analyze(query)      │
│      ├── 📰 news_sentiment = news_agent.analyze(query)     │
│      ├── 🐦 social_sentiment = social_agent.analyze(query) │
│      │                                                     │
│      └── 🤖 prediction = predictor_agent.predict(...)      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
📊 MARKET AGENT - Parallel Data Collection
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  🔍 Auto-detect Available Providers:                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Coinbase   │  │ CryptoComp  │  │   Binance   │        │
│  │    REST     │  │     API     │  │    Mock     │        │
│  │             │  │             │  │             │        │
│  │ ✅ Active   │  │ ✅ Active   │  │ ✅ Active   │        │
│  │ $63,500 BTC │  │ $63,450 BTC │  │ $63,600 BTC │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  📈 Aggregated Result:                                     │
│  {                                                          │
│    "aggregated_data": {                                     │
│      "BTC_USD": {                                          │
│        "price": 63516.67,                                  │
│        "confidence": 0.94,                                 │
│        "sources_count": 3                                  │
│      }                                                     │
│    },                                                      │
│    "individual_sources": {...},                           │
│    "market_signals": {...}                                │
│  }                                                         │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
📰 NEWS AGENT + 🐦 SOCIAL AGENT
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  📰 News Sentiment: "Positive momentum, institutional      │
│      adoption increasing..."                               │
│                                                             │
│  🐦 Social Sentiment: "Bullish sentiment on Reddit,       │
│      Twitter mentions up 15%..."                          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
🤖 PREDICTOR AGENT
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Input:                                                     │
│  ├── 📊 Market Data (aggregated + confidence)              │
│  ├── 📰🐦 Combined Sentiment                               │
│  ├── 🎯 Style: "aggressive"                                │
│  └── 🤖 Provider: "openai/anthropic/google..."             │
│                                                             │
│  🧠 LLM Processing:                                         │
│  "Based on high confidence market data (0.94) showing     │
│   $63,516 BTC with positive sentiment across news and     │
│   social channels, aggressive strategy recommendation..."   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
📋 FINAL OUTPUT
┌─────────────────────────────────────────────────────────────┐
│  📊 Market Data Summary                                     │
│  📰🐦 Sentiment Analysis                                   │
│  📈 Final Recommendation:                                   │
│      "Strong BUY signal with 85% confidence..."           │
└─────────────────────────────────────────────────────────────┘
```

## 🏛️ Architettura dei Provider (Market Agent)

```
┌─────────────────────────────────────────────────────────────────┐
│                    📊 MARKET AGENT                             │
│                                                                 │
│  🔍 Provider Detection Logic:                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ def _setup_providers():                                     ││
│  │   ├── 🔑 Check CDP_API_KEY_NAME + CDP_API_PRIVATE_KEY      ││
│  │   │   └── ✅ Setup Coinbase Advanced Trade                 ││
│  │   ├── 🔑 Check CRYPTOCOMPARE_API_KEY                       ││
│  │   │   └── ✅ Setup CryptoCompare                           ││
│  │   └── 🔑 Check BINANCE_API_KEY (future)                    ││
│  │       └── ✅ Setup Binance API                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  📡 Data Flow:                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Provider 1 │───▶│             │◀───│  Provider 2 │        │
│  │  Coinbase   │    │  AGGREGATOR │    │ CryptoComp  │        │
│  │             │    │             │    │             │        │
│  │ Real-time   │    │ ┌─────────┐ │    │ Real-time   │        │
│  │ Market Data │    │ │Confidence│ │    │ Market Data │        │
│  └─────────────┘    │ │Scoring  │ │    └─────────────┘        │
│                     │ │         │ │                           │
│  ┌─────────────┐    │ │ Spread  │ │    ┌─────────────┐        │
│  │  Provider 3 │───▶│ │Analysis │ │◀───│  Provider N │        │
│  │  Binance    │    │ │         │ │    │   Future    │        │
│  │             │    │ └─────────┘ │    │             │        │
│  │ Mock Data   │    │             │    │             │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Signers Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     🔐 SIGNERS ECOSYSTEM                       │
│                                                                 │
│  📁 src/app/signers/market_signers/                            │
│  │                                                             │
│  ├── 🏦 coinbase_rest_signer.py                                │
│  │   ├── 🔑 Uses: CDP_API_KEY_NAME + CDP_API_PRIVATE_KEY      │
│  │   ├── 📡 RESTClient from coinbase.rest                     │
│  │   ├── 📊 get_asset_info() → Real Coinbase data            │
│  │   └── 📈 get_multiple_assets() → Bulk data                 │
│  │                                                             │
│  ├── 📊 cryptocompare_signer.py                               │
│  │   ├── 🔑 Uses: CRYPTOCOMPARE_API_KEY                       │
│  │   ├── 📡 Direct HTTP requests                              │
│  │   ├── 💰 get_crypto_prices() → Multi-currency             │
│  │   └── 🏆 get_top_cryptocurrencies() → Market cap         │
│  │                                                             │
│  └── 🟡 binance_signer.py                                     │
│      ├── 🔑 Uses: BINANCE_API_KEY (future)                    │
│      ├── 📡 Mock implementation                               │
│      ├── 🎭 Simulated market data                            │
│      └── 📈 Compatible interface                              │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Future Enhancement: Async Flow

```
                    📱 USER REQUEST
                          │
                          ▼
                 🔧 TOOL AGENT (async)
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    📊 Market         📰 News          🐦 Social
    Agent (async)     Agent (async)    Agent (async)
         │                │                │
    ┌────┼────┐           │                │
    ▼    ▼    ▼           │                │
 Coinbase │ Binance       │                │
    CC    │               │                │
         ▼▼▼              ▼                ▼
    🔄 Parallel      📰 Sentiment     🐦 Sentiment
    Aggregation      Analysis         Analysis
         │                │                │
         └────────────────┼────────────────┘
                          ▼
                  🤖 PREDICTOR AGENT
                     (LLM Analysis)
                          │
                          ▼
                    📋 FINAL RESULT
                  (JSON + Confidence)
```

## 📊 Data Flow Example

```
Input: "Analyze Bitcoin aggressive strategy"
│
├── 📊 Market Agent Output:
│   {
│     "aggregated_data": {
│       "BTC_USD": {"price": 63516.67, "confidence": 0.94}
│     },
│     "individual_sources": {
│       "coinbase": {"price": 63500, "volume": "1.2M"},
│       "cryptocompare": {"price": 63450, "volume": "N/A"},
│       "binance": {"price": 63600, "volume": "2.1M"}
│     },
│     "market_signals": {
│       "spread_analysis": "Low spread (0.24%) - healthy liquidity",
│       "price_divergence": "Max deviation: 0.24% - Normal range"
│     }
│   }
│
├── 📰 News Sentiment: "Positive institutional adoption news..."
├── 🐦 Social Sentiment: "Bullish Reddit sentiment, +15% mentions"
│
└── 🤖 Predictor Output:
    "📈 Strong BUY recommendation based on:
     - High confidence market data (94%)
     - Positive news sentiment
     - Bullish social indicators
     - Low spread indicates healthy liquidity
     
     Aggressive Strategy: Consider 15-20% portfolio allocation"
```

---
*Diagrammi creati: 2025-09-23*
*Sistema: upo-appAI Market Analysis Platform*