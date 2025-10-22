# 📊 Architettura e Flussi dell'App upo-appAI

## 🏗️ Diagramma Architettura Generale

```
┌─────────────────────────────────────────────────────────────────┐
│                   🌐 INTERFACCE UTENTE                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             💬 Gradio Web Interface                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────────────┐   │ │
│  │  │  Chat    │  │  Model   │  │  Strategy (Strategy)  │   │ │
│  │  │ History  │  │Dropdown  │  │  - Conservative       │   │ │
│  │  │          │  │          │  │  - Aggressive         │   │ │
│  │  └──────────┘  └──────────┘  └───────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             📱 Telegram Bot Interface                      │ │
│  │         (Mini App con integrazione Gradio)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 CHAT MANAGER                              │
│               (Gestione Conversazioni)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Mantiene storico messaggi (history)                   │   │
│  │ - Gestisce input Pipeline (PipelineInputs)              │   │
│  │ - Salva/Carica chat (JSON)                              │   │
│  │ - Interfaccia Gradio (gradio_build_interface)           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🔄 AGNO WORKFLOW PIPELINE                   │
│                  (Orchestrazione Asincrona)                     │
│                                                                 │
│  Step 1: 🔍 Query Check         → Verifica query crypto        │
│  Step 2: 🤔 Condition Check     → Valida se procedere          │
│  Step 3: 📊 Info Recovery       → Team di raccolta dati        │
│  Step 4: 📝 Report Generation   → Genera report finale         │
│                                                                 │
│  Pipeline Events: QUERY_CHECK | QUERY_ANALYZER |               │
│                   INFO_RECOVERY | REPORT_GENERATION |          │
│                   TOOL_USED | RUN_FINISHED                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   🤖 AGNO AGENT ECOSYSTEM                       │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │             👔 TEAM LEADER (Agno Team)                    │  │
│ │  - Coordina Market, News, Social Agents                   │  │
│ │  - Tools: ReasoningTools, PlanMemoryTool,                 │  │
│ │           CryptoSymbolsTools                              │  │
│ │  - Model: Configurabile (team_leader_model)               │  │
│ └───────────────────────────────────────────────────────────┘  │
│         │                      │                      │         │
│         ▼                      ▼                      ▼         │
│ ┌─────────────┐       ┌─────────────┐       ┌─────────────┐   │
│ │   MARKET    │       │    NEWS     │       │   SOCIAL    │   │
│ │   AGENT     │       │   AGENT     │       │   AGENT     │   │
│ │  (Agno)     │       │  (Agno)     │       │  (Agno)     │   │
│ │             │       │             │       │             │   │
│ │ Tool:       │       │ Tool:       │       │ Tool:       │   │
│ │ MarketAPIs  │       │ NewsAPIs    │       │ SocialAPIs  │   │
│ │ Tool        │       │ Tool        │       │ Tool        │   │
│ └─────────────┘       └─────────────┘       └─────────────┘   │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │           � QUERY CHECK AGENT (Agno Agent)              │  │
│ │  - Valida se la query è relativa a crypto                │  │
│ │  - Output Schema: QueryOutputs (is_crypto: bool)          │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │        📋 REPORT GENERATOR AGENT (Agno Agent)            │  │
│ │  - Genera report finale basato su dati raccolti           │  │
│ │  - Applica strategia (Conservative/Aggressive)            │  │
│ └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flusso di Esecuzione Dettagliato

```
👤 USER REQUEST
    │
    │ "Analizza Bitcoin con strategia aggressiva"
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   � CHAT MANAGER                               │
│                                                                  │
│  - Riceve messaggio utente                                      │
│  - Gestisce history della conversazione                         │
│  - Prepara PipelineInputs con:                                  │
│    * user_query: "Analizza Bitcoin..."                          │
│    * strategy: "aggressive"                                     │
│    * models: team_leader_model, team_model, etc.                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│              🔄 AGNO WORKFLOW PIPELINE                          │
│                                                                  │
│  Run ID: [3845] Pipeline query: "Analizza Bitcoin..."          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 1: 🔍 QUERY CHECK (Query Check Agent)              │  │
│  │                                                          │  │
│  │  Input: QueryInputs(user_query, strategy)               │  │
│  │  Agent: query_analyzer_model (Agno Agent)               │  │
│  │  Output: QueryOutputs(response, is_crypto: bool)        │  │
│  │                                                          │  │
│  │  Result: {"is_crypto": true, "response": "..."}         │  │
│  │  Event: QUERY_CHECK completed                           │  │
│  └──────────────────────────────────────────────────────────┘  │
    │
    ▼
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 2: 🤔 CONDITION CHECK                               │  │
│  │                                                          │  │
│  │  Valida: previous_step_content.is_crypto                │  │
│  │  If False → StopOutput(stop=True)                       │  │
│  │  If True  → Continua al prossimo step                   │  │
│  └──────────────────────────────────────────────────────────┘  │
    │
    ▼
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 3: 📊 INFO RECOVERY (Team)                         │  │
│  │                                                          │  │
│  │  👔 Team Leader coordina:                               │  │
│  │     ├── 📈 Market Agent → MarketAPIsTool                │  │
│  │     ├── 📰 News Agent   → NewsAPIsTool                  │  │
│  │     └── 🐦 Social Agent → SocialAPIsTool                │  │
│  │                                                          │  │
│  │  Tools disponibili al Team Leader:                      │  │
│  │     - ReasoningTools (ragionamento)                     │  │
│  │     - PlanMemoryTool (memoria del piano)                │  │
│  │     - CryptoSymbolsTools (simboli crypto)               │  │
│  │                                                          │  │
│  │  Events: TOOL_USED per ogni chiamata tool               │  │
│  │  Event: INFO_RECOVERY completed                         │  │
│  └──────────────────────────────────────────────────────────┘  │
    │
    ▼
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 4: 📝 REPORT GENERATION (Report Generator Agent)   │  │
│  │                                                          │  │
│  │  Input: Tutti i dati raccolti da Info Recovery          │  │
│  │  Agent: report_generation_model (Agno Agent)            │  │
│  │  Strategia: Applicata dal prompt (aggressive)           │  │
│  │                                                          │  │
│  │  Output: Report finale con raccomandazioni              │  │
│  │  Event: REPORT_GENERATION completed                     │  │
│  └──────────────────────────────────────────────────────────┘  │
    │
    ▼
│  Event: RUN_FINISHED                                            │
│  Return: Final report string (rimozione tag <think>)            │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
📋 FINAL OUTPUT TO USER
┌─────────────────────────────────────────────────────────────────┐
│  📊 Analisi Bitcoin (BTC)                                       │
│                                                                  │
│  � Dati di Mercato:                                            │
│     - Prezzo: $63,516 (aggregato da 4 fonti)                   │
│     - Volume 24h: $2.1M                                         │
│     - Confidence: 94%                                           │
│                                                                  │
│  📰 Sentiment News: Positivo (istituzionale in crescita)       │
│  🐦 Sentiment Social: Bullish (Reddit/Twitter +15%)            │
│                                                                  │
│  🎯 Raccomandazione (Strategia Aggressiva):                    │
│     STRONG BUY - Allocazione 15-20% del portfolio              │
│                                                                  │
│  💭 Ragionamento: [dettagli dell'analisi...]                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🏛️ Architettura API e Tools

```
┌─────────────────────────────────────────────────────────────────┐
│                  � API TOOLS ARCHITECTURE                      │
│                  (Agno Toolkit Integration)                     │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         📊 MarketAPIsTool (Agno Toolkit)              │    │
│  │                                                        │    │
│  │  Tools disponibili:                                    │    │
│  │  - get_product(asset_id)                              │    │
│  │  - get_products(asset_ids)                            │    │
│  │  - get_historical_prices(asset_id, limit)             │    │
│  │  - get_products_aggregated(asset_ids)                 │    │
│  │  - get_historical_prices_aggregated(asset_id, limit)  │    │
│  │                                                        │    │
│  │  🔄 WrapperHandler gestisce:                          │    │
│  │  ┌──────────────┐  ┌──────────────┐                   │    │
│  │  │  Binance     │  │  YFinance    │                   │    │
│  │  │  Wrapper     │  │  Wrapper     │                   │    │
│  │  └──────────────┘  └──────────────┘                   │    │
│  │  ┌──────────────┐  ┌──────────────┐                   │    │
│  │  │  CoinBase    │  │CryptoCompare │                   │    │
│  │  │  Wrapper     │  │  Wrapper     │                   │    │
│  │  └──────────────┘  └──────────────┘                   │    │
│  │                                                        │    │
│  │  Retry Logic: 3 tentativi per wrapper, 2s delay       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         📰 NewsAPIsTool (Agno Toolkit)                │    │
│  │                                                        │    │
│  │  🔄 WrapperHandler gestisce:                          │    │
│  │  - NewsAPI Wrapper                                     │    │
│  │  - GoogleNews Wrapper                                  │    │
│  │  - DuckDuckGo Wrapper                                  │    │
│  │  - CryptoPanic Wrapper                                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         🐦 SocialAPIsTool (Agno Toolkit)              │    │
│  │                                                        │    │
│  │  🔄 WrapperHandler gestisce:                          │    │
│  │  - Reddit Wrapper                                      │    │
│  │  - X (Twitter) Wrapper                                 │    │
│  │  - 4chan Wrapper                                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         🔣 CryptoSymbolsTools (Agno Toolkit)          │    │
│  │  - Gestisce simboli e nomi delle criptovalute          │    │
│  │  - Carica da resources/cryptos.csv                     │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## � WrapperHandler Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    � WRAPPER HANDLER                           │
│              (Resilient API Call Management)                    │
│                                                                 │
│  Input: List[WrapperType]                                      │
│         try_per_wrapper: int = 3                               │
│         retry_delay: int = 2                                   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ def try_call(func: Callable) -> OutputType:              │ │
│  │                                                           │ │
│  │   for wrapper in wrappers:                               │ │
│  │     for attempt in range(try_per_wrapper):               │ │
│  │       try:                                               │ │
│  │         result = func(wrapper)                           │ │
│  │         return result  # ✅ Success                      │ │
│  │       except Exception as e:                             │ │
│  │         log_error(e)                                     │ │
│  │         sleep(retry_delay)                               │ │
│  │         continue  # � Retry                             │ │
│  │                                                           │ │
│  │     # Switch to next wrapper                             │ │
│  │                                                           │ │
│  │   raise Exception("All wrappers failed")  # ❌ All fail  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Esempio Flusso:                                               │
│  ┌─────────┐  Fail   ┌─────────┐  Fail   ┌─────────┐         │
│  │Binance  │────────▶│YFinance │────────▶│CoinBase │  ✅     │
│  │(3 tries)│         │(3 tries)│         │(Success)│         │
│  └─────────┘         └─────────┘         └─────────┘         │
│                                                                 │
│  Features:                                                     │
│  ✅ Automatic failover tra providers                           │
│  ✅ Retry logic configurabile                                  │
│  ✅ Logging dettagliato degli errori                           │
│  ✅ Type-safe con Generics                                     │
└─────────────────────────────────────────────────────────────────┘
```

## � Data Aggregation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              📊 PRODUCT INFO AGGREGATION                        │
│                                                                 │
│  Input: dict[provider_name, list[ProductInfo]]                 │
│                                                                 │
│  Provider A: BTC → {price: 63500, volume: 1.2M}                │
│  Provider B: BTC → {price: 63450, volume: N/A}                 │
│  Provider C: BTC → {price: 63600, volume: 2.1M}                │
│  Provider D: BTC → {price: 63550, volume: 1.8M}                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Aggregation Logic:                                        │ │
│  │                                                           │ │
│  │ 1. Group by symbol (BTC, ETH, etc.)                      │ │
│  │                                                           │ │
│  │ 2. Aggregate Volume:                                     │ │
│  │    avg_volume = sum(volumes) / count(providers)          │ │
│  │                                                           │ │
│  │ 3. Aggregate Price (weighted by volume):                 │ │
│  │    weighted_price = sum(price * volume) / sum(volume)    │ │
│  │                                                           │ │
│  │ 4. Calculate Confidence:                                 │ │
│  │    - Based on price spread                               │ │
│  │    - Number of sources                                   │ │
│  │    - Volume consistency                                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Output: list[ProductInfo]                                     │
│  {                                                              │
│    "id": "BTC_AGGREGATED",                                     │
│    "symbol": "BTC",                                            │
│    "price": 63516.67,  # Weighted average                      │
│    "volume_24h": 1.7M,  # Average volume                       │
│    "currency": "USD",                                          │
│    "confidence": 0.94  # High confidence (low spread)          │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│           📈 HISTORICAL PRICE AGGREGATION                       │
│                                                                 │
│  Input: dict[provider_name, list[Price]]                       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Aggregation Logic:                                        │ │
│  │                                                           │ │
│  │ 1. Align by timestamp (YYYY-MM-DD HH:MM)                 │ │
│  │                                                           │ │
│  │ 2. For each timestamp, calculate mean of:                │ │
│  │    - high                                                 │ │
│  │    - low                                                  │ │
│  │    - open                                                 │ │
│  │    - close                                                │ │
│  │    - volume                                               │ │
│  │                                                           │ │
│  │ 3. Handle missing data gracefully                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Output: list[Price] (aggregated by timestamp)                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Configuration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  ⚙️ APP CONFIG (configs.yaml)                   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  port: 7860  # Gradio server port                     │    │
│  │  gradio_share: false  # Public sharing                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  models:  # LLM Models Configuration                  │    │
│  │    - label: "Qwen 3 (4B)"                             │    │
│  │      provider: "ollama"                               │    │
│  │      model_id: "qwen3:4b"                             │    │
│  │    - label: "Qwen 3 (1.7B)"                           │    │
│  │      provider: "ollama"                               │    │
│  │      model_id: "qwen3:1.7b"                           │    │
│  │    - label: "GPT-4 Turbo"                             │    │
│  │      provider: "openai"                               │    │
│  │      model_id: "gpt-4-turbo"                          │    │
│  │      api_key_env: "OPENAI_API_KEY"                    │    │
│  │    # ... altri modelli (Anthropic, Google, etc.)      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  strategies:  # Investment Strategies                 │    │
│  │    - label: "Conservative"                            │    │
│  │      description: "Low risk, stable returns..."       │    │
│  │    - label: "Aggressive"                              │    │
│  │      description: "High risk, high potential..."      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  agents:  # Agent-specific configurations             │    │
│  │    team_model: "qwen3:4b"                             │    │
│  │    team_leader_model: "qwen3:4b"                      │    │
│  │    query_analyzer_model: "qwen3:1.7b"                 │    │
│  │    report_generation_model: "qwen3:4b"                │    │
│  │    strategy: "Conservative"                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  api:  # API Configuration                            │    │
│  │    retry_attempts: 3                                  │    │
│  │    retry_delay_seconds: 2                             │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              🔐 ENVIRONMENT VARIABLES (.env)                    │
│                                                                 │
│  # Market APIs                                                 │
│  CDP_API_KEY_NAME=...          # Coinbase                      │
│  CDP_API_PRIVATE_KEY=...       # Coinbase                      │
│  CRYPTOCOMPARE_API_KEY=...     # CryptoCompare                 │
│  BINANCE_API_KEY=...           # Binance (future)              │
│                                                                 │
│  # News APIs                                                   │
│  NEWS_API_KEY=...              # NewsAPI                       │
│  CRYPTOPANIC_API_KEY=...       # CryptoPanic                   │
│                                                                 │
│  # Social APIs                                                 │
│  REDDIT_CLIENT_ID=...          # Reddit                        │
│  REDDIT_CLIENT_SECRET=...      # Reddit                        │
│  X_BEARER_TOKEN=...            # Twitter/X                     │
│                                                                 │
│  # LLM Providers                                               │
│  OPENAI_API_KEY=...            # OpenAI                        │
│  ANTHROPIC_API_KEY=...         # Anthropic                     │
│  GOOGLE_API_KEY=...            # Google                        │
│                                                                 │
│  # Telegram Bot                                                │
│  TELEGRAM_BOT_TOKEN=...        # Telegram Bot                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🗂️ Struttura del Progetto

```
upo-appAI/
│
├── 📁 src/app/                      # Codice principale
│   ├── __main__.py                  # Entry point (Gradio + Telegram)
│   ├── configs.py                   # Gestione configurazioni
│   │
│   ├── 📁 agents/                   # Sistema di agenti Agno
│   │   ├── core.py                  # PipelineInputs, QueryInputs/Outputs
│   │   ├── pipeline.py              # Workflow Pipeline con Agno
│   │   ├── plan_memory_tool.py      # Tool per memoria del piano
│   │   └── 📁 prompts/              # Prompt per gli agenti
│   │       ├── query_check.txt      # Prompt Query Checker
│   │       ├── team_leader.txt      # Prompt Team Leader
│   │       ├── team_market.txt      # Prompt Market Agent
│   │       ├── team_news.txt        # Prompt News Agent
│   │       ├── team_social.txt      # Prompt Social Agent
│   │       └── report_generation.txt # Prompt Report Generator
│   │
│   ├── 📁 api/                      # Layer API e Wrappers
│   │   ├── wrapper_handler.py       # Pattern WrapperHandler generico
│   │   │
│   │   ├── 📁 core/                 # Interfacce base e modelli
│   │   │   ├── markets.py           # MarketWrapper, ProductInfo, Price
│   │   │   ├── news.py              # NewsWrapper, NewsItem
│   │   │   └── social.py            # SocialWrapper, SocialPost
│   │   │
│   │   ├── 📁 markets/              # Implementazioni Market API
│   │   │   ├── binance.py           # BinanceWrapper
│   │   │   ├── coinbase.py          # CoinBaseWrapper
│   │   │   ├── cryptocompare.py     # CryptoCompareWrapper
│   │   │   └── yfinance.py          # YFinanceWrapper
│   │   │
│   │   ├── 📁 news/                 # Implementazioni News API
│   │   │   ├── newsapi.py           # NewsAPIWrapper
│   │   │   ├── googlenews.py        # GoogleNewsWrapper
│   │   │   ├── duckduckgo.py        # DuckDuckGoWrapper
│   │   │   └── cryptopanic_api.py   # CryptoPanicWrapper
│   │   │
│   │   ├── 📁 social/               # Implementazioni Social API
│   │   │   ├── reddit.py            # RedditWrapper
│   │   │   ├── x.py                 # XWrapper (Twitter)
│   │   │   └── chan.py              # 4ChanWrapper
│   │   │
│   │   └── 📁 tools/                # Agno Toolkits
│   │       ├── market_tool.py       # MarketAPIsTool (Agno Toolkit)
│   │       ├── news_tool.py         # NewsAPIsTool (Agno Toolkit)
│   │       ├── social_tool.py       # SocialAPIsTool (Agno Toolkit)
│   │       └── symbols_tool.py      # CryptoSymbolsTools (Agno Toolkit)
│   │
│   └── 📁 interface/                # Interfacce utente
│       ├── chat.py                  # ChatManager (Gradio)
│       └── telegram_app.py          # TelegramApp (Bot)
│
├── 📁 tests/                        # Test suite completa
│   ├── conftest.py                  # Configurazione pytest
│   ├── 📁 agents/                   # Test agenti
│   ├── 📁 api/                      # Test API wrappers
│   ├── 📁 tools/                    # Test tools
│   └── 📁 utils/                    # Test utilities
│
├── 📁 demos/                        # Script di esempio
│   ├── agno_agent.py                # Demo Agno Agent
│   ├── agno_workflow.py             # Demo Agno Workflow
│   ├── coinbase_demo.py             # Demo Coinbase API
│   ├── cryptocompare_demo.py        # Demo CryptoCompare API
│   └── market_providers_api_demo.py # Demo aggregazione provider
│
├── 📁 resources/                    # Risorse statiche
│   └── cryptos.csv                  # Database simboli crypto
│
├── 📁 docs/                         # Documentazione
│   ├── App_Architecture_Diagrams.md # Questo file
│   └── Progetto Esame.md            # Specifiche progetto
│
├── configs.yaml                     # Configurazione app (modelli, strategie)
├── .env                             # Variabili d'ambiente (API keys)
├── .env.example                     # Template per .env
├── pyproject.toml                   # Dipendenze Python (uv/pip)
├── Dockerfile                       # Container Docker
├── docker-compose.yaml              # Orchestrazione Docker
└── README.md                        # Documentazione principale
```

## 🔑 Componenti Chiave

### 1. **Agno Framework Integration**
L'applicazione utilizza il framework **Agno** per gestire:
- **Agent**: Singoli agenti con modelli LLM specifici
- **Team**: Coordinazione di più agenti sotto un Team Leader
- **Workflow**: Pipeline asincrone con step condizionali
- **Toolkit**: Integrazione tools con retry logic
- **RunEvent**: Sistema di eventi per monitoraggio

### 2. **WrapperHandler Pattern**
Pattern generico per gestire multiple implementazioni API con:
- Failover automatico tra provider
- Retry logic configurabile
- Type safety con Generics
- Logging dettagliato

### 3. **Data Aggregation**
Sistema sofisticato di aggregazione che:
- Combina dati da multiple fonti
- Calcola confidence score
- Gestisce dati mancanti/inconsistenti
- Fornisce weighted averages

### 4. **Multi-Interface Support**
Due interfacce integrate:
- **Gradio Web UI**: Chat interface con dropdown per modelli/strategie
- **Telegram Bot**: Bot con Mini App integrato

### 5. **Configuration Management**
Sistema a due livelli:
- **configs.yaml**: Configurazioni applicazione (modelli, strategie, agenti)
- **.env**: Secrets e API keys (caricato con dotenv)

## 🚀 Deployment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    🐳 DOCKER DEPLOYMENT                         │
│                                                                 │
│  1. Load .env variables                                        │
│  2. Build Docker image (Python 3.11)                           │
│  3. Install dependencies (pyproject.toml)                      │
│  4. Copy src/, configs.yaml, resources/                        │
│  5. Expose port 7860 (Gradio)                                  │
│  6. Run: python -m src.app                                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  docker-compose up --build -d                            │  │
│  │                                                          │  │
│  │  Services:                                               │  │
│  │  - app: Main application (Gradio + Telegram)            │  │
│  │  - Networks: Bridge mode                                │  │
│  │  - Volumes: .env mounted                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 💻 LOCAL DEVELOPMENT (UV)                       │
│                                                                 │
│  1. Install uv package manager                                 │
│  2. uv venv (create virtual environment)                       │
│  3. uv pip install -e . (editable install)                     │
│  4. uv run src/app (run application)                           │
│                                                                 │
│  Benefits:                                                     │
│  ✅ Fast dependency resolution                                 │
│  ✅ Automatic PYTHONPATH setup                                 │
│  ✅ Editable mode for development                              │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Workflow Execution Model

L'applicazione utilizza un modello di esecuzione **Asincrono** basato su Agno Workflow:

```python
# Pipeline di esecuzione
async def interact_async():
    workflow = Workflow(steps=[
        query_check,         # Step 1: Verifica query
        condition_query_ok,  # Step 2: Condizione
        info_recovery,       # Step 3: Team di raccolta
        report_generation    # Step 4: Report finale
    ])
    
    # Esecuzione con streaming
    iterator = await workflow.arun(
        query,
        stream=True,
        stream_intermediate_steps=True
    )
    
    # Event handling
    async for event in iterator:
        if event.event == PipelineEvent.TOOL_USED:
            log(f"Tool: {event.tool.tool_name}")
        elif event.event == WorkflowRunEvent.step_completed:
            log(f"Step: {event.step_name} completed")
```

**Vantaggi:**
- ⚡ Esecuzione asincrona per migliori performance
- 📊 Streaming di eventi intermedi
- 🎯 Gestione condizionale del flusso
- 🔄 Retry automatico sui tools

## 📈 Future Enhancements

Possibili miglioramenti architetturali:

1. **Parallel Tool Execution**: Esecuzione parallela di Market/News/Social agents
2. **Caching Layer**: Redis/Memcached per ridurre chiamate API
3. **Database Integration**: PostgreSQL per storico analisi
4. **Real-time WebSocket**: Aggiornamenti live prezzi
5. **ML Model Integration**: Modelli predittivi custom (LSTM, Transformer)
6. **Advanced Aggregation**: Confidence scoring migliorato con ML
7. **User Profiles**: Personalizzazione strategie per utente
8. **Backtesting Module**: Validazione strategie su dati storici

---
*Documento aggiornato: 2025-10-22*
*Sistema: upo-appAI Crypto Analysis Platform*
*Framework: Agno (Agentic AI) + Gradio + Telegram*