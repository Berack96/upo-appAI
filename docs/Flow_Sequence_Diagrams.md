# Diagrammi di Flusso e Sequenza (Sintesi)

Documentazione breve con blocchi testuali e mermaid per flussi principali.

## Flusso Gradio Chat

```mermaid
flowchart LR
  U[User] --> CH(ChatInterface)
  CH --> RESP[gradio_respond]
  RESP --> PL(Pipeline.interact)
  PL --> WF(Workflow run)
  WF --> OUT(Report)
  CH --> HIST[history update]
```

## Flusso Telegram Bot

```
/start
  │
  ├─> CONFIGS state
  │    ├─ Model Team ↔ choose_team(index)
  │    ├─ Model Output ↔ choose_team_leader(index)
  │    └─ Strategy ↔ choose_strategy(index)
  │
  └─> Text message → __start_team
        └─ run team → Pipeline.interact_async
             ├─ build_workflow
             ├─ stream events (Query Check → Gate → Info Recovery → Report)
             └─ send PDF (markdown_pdf)
```

## Pipeline Steps (Workflow)

```mermaid
flowchart TD
  A[QueryInputs] --> B[Query Check Agent]
  B -->|is_crypto true| C[Team Info Recovery]
  B -->|is_crypto false| STOP((Stop))
  C --> D[Report Generation Agent]
  D --> OUT[Markdown Report]
```

## Team Leader Loop (PlanMemoryTool)

```
Initialize Plan with tasks
Loop until no pending tasks:
  - Get next pending task
  - Dispatch to specific Agent (Market/News/Social)
  - Update task status (completed/failed)
  - If failed & scope comprehensive → add retry task
After loop:
  - List all tasks & results
  - Synthesize final report
```

## Tools Aggregazione

```mermaid
flowchart LR
  TL[Team Leader] --> MT[MarketAPIsTool]
  TL --> NT[NewsAPIsTool]
  TL --> ST[SocialAPIsTool]
  MT --> WH(WrapperHandler)
  NT --> WH
  ST --> WH
  WH --> W1[Binance]
  WH --> W2[Coinbase]
  WH --> W3[CryptoCompare]
  WH --> W4[YFinance]
  WH --> N1[NewsAPI]
  WH --> N2[GoogleNews]
  WH --> N3[CryptoPanic]
  WH --> N4[DuckDuckGo]
  WH --> S1[Reddit]
  WH --> S2[X]
  WH --> S3[4chan]
```