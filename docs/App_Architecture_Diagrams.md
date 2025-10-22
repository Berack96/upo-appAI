# 📊 Architettura upo-appAI

## 🏗️ Architettura Generale

```
INTERFACCE UTENTE
├── 💬 Gradio Web (Chat + Dropdown modelli/strategie)
└── 📱 Telegram Bot (Mini App)
       │
       ▼
CHAT MANAGER
├── Storico messaggi
├── Gestione PipelineInputs
└── Salva/Carica chat
       │
       ▼
AGNO WORKFLOW PIPELINE (4 Steps)
├── 1. Query Check → Verifica crypto
├── 2. Condition → Valida procedere
├── 3. Info Recovery → Team raccolta dati
└── 4. Report Generation → Report finale
       │
       ▼
AGNO AGENT ECOSYSTEM
├── 👔 TEAM LEADER (coordina Market, News, Social)
│   Tools: ReasoningTools, PlanMemoryTool, CryptoSymbolsTools
├── 📈 MARKET AGENT → MarketAPIsTool
├── 📰 NEWS AGENT → NewsAPIsTool
├── 🐦 SOCIAL AGENT → SocialAPIsTool
├── 🔍 QUERY CHECK AGENT → QueryOutputs (is_crypto: bool)
└── 📋 REPORT GENERATOR AGENT → Strategia applicata
```

## 🔄 Flusso Esecuzione

**Input:** "Analizza Bitcoin con strategia aggressiva"

1. CHAT MANAGER riceve e prepara PipelineInputs
2. WORKFLOW PIPELINE esegue 4 step:
   - Query Check: valida `is_crypto: true`
   - Condition: se false, termina
   - Info Recovery: Team raccoglie dati
   - Report Generation: genera report
3. OUTPUT: Report con analisi + raccomandazioni

## 🏛️ Architettura API

**Tools (Agno Toolkit):**
- MarketAPIsTool: Binance, YFinance, CoinBase, CryptoCompare
- NewsAPIsTool: NewsAPI, GoogleNews, DuckDuckGo, CryptoPanic
- SocialAPIsTool: Reddit, X, 4chan
- CryptoSymbolsTools: `resources/cryptos.csv`

**WrapperHandler:** Failover automatico (3 tentativi/wrapper, 2s delay)

## 📊 Data Aggregation

**ProductInfo:**
- Volume: media tra sources
- Price: weighted average (price × volume)
- Confidence: spread + numero sources

**Historical Price:**
- Align per timestamp
- Media: high, low, open, close, volume

## 🎯 Configuration

**configs.yaml:**
```yaml
port: 8000
models: [Ollama, OpenAI, Anthropic, Google]
strategies: [Conservative, Aggressive]
agents: {team_model, team_leader_model, ...}
api: {retry_attempts: 3, retry_delay_seconds: 2}
```

**.env (API Keys):**
- Market: CDP_API_KEY, CRYPTOCOMPARE_API_KEY, ...
- News: NEWS_API_KEY, CRYPTOPANIC_API_KEY, ...
- Social: REDDIT_CLIENT_ID, X_API_KEY, ...
- LLM: OPENAI_API_KEY, ANTHROPIC_API_KEY, ...
- Bot: TELEGRAM_BOT_TOKEN

## 🗂️ Struttura Progetto

```
src/app/
├── __main__.py
├── configs.py
├── agents/
│   ├── core.py
│   ├── pipeline.py
│   ├── plan_memory_tool.py
│   └── prompts/
├── api/
│   ├── wrapper_handler.py
│   ├── core/ (markets, news, social)
│   ├── markets/ (Binance, CoinBase, CryptoCompare, YFinance)
│   ├── news/ (NewsAPI, GoogleNews, DuckDuckGo, CryptoPanic)
│   ├── social/ (Reddit, X, 4chan)
│   └── tools/ (Agno Toolkits)
└── interface/ (chat.py, telegram_app.py)

tests/
demos/
resources/cryptos.csv
docs/
configs.yaml
.env
```

## 🔑 Componenti Chiave

1. **Agno Framework**: Agent, Team, Workflow, Toolkit, RunEvent
2. **WrapperHandler**: Failover, Retry logic, Type safety
3. **Data Aggregation**: Multiple sources, Confidence score
4. **Multi-Interface**: Gradio + Telegram
5. **Configuration**: configs.yaml + .env

## 🚀 Deployment

**Docker:**
```bash
docker-compose up --build -d
```

**Local (UV):**
```bash
uv venv
uv pip install -e .
uv run src/app
```

## 🎯 Workflow Asincrono

```python
workflow = Workflow(steps=[
    query_check, condition,
    info_recovery, report_generation
])

iterator = await workflow.arun(query, stream=True)

async for event in iterator:
    if event.event == PipelineEvent.TOOL_USED:
        log(f"Tool: {event.tool.tool_name}")
```

**Vantaggi:** Asincrono, Streaming, Condizionale, Retry

## 📈 Future Enhancements

- Parallel Tool Execution
- Caching (Redis)
- Database (PostgreSQL)
- Real-time WebSocket
- ML Models
- User Profiles
- Backtesting
