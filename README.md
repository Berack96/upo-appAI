# **Agente di Analisi e Consulenza Crypto**
Questa è la repository per l'esame di Applicazioni Intelligenti che consiste in:
- Progetto per 2/3 del voto.
- Orale per 1/3 dei punti composto da:
  - Presentazione (come se lo facessimo ad un cliente) di gruppo
  - Orale singolo con domande del corso (teoria e strumenti visti)

L'obiettivo è quello di creare un sistema di consulenza finanziaria basato su LLM Agents che analizza il mercato delle criptovalute per fornire consigli di investimento personalizzati. Inoltre il sistema deve dimostrare la capacità di ragionare, gestire la persistenza dei dati, utilizzare fonti esterne e presentare un'analisi comprensibile e razionale, offrendo sia una consulenza ad ampio spettro che su una singola criptovaluta.

# **Indice**
- [Installazione](#installazione)
  - [1. Configurazioni](#1-configurazioni)
  - [2. Ollama](#2-ollama)
  - [3. Docker](#3-docker)
  - [4. UV (solo per sviluppo locale)](#4-uv-solo-per-sviluppo-locale)
- [Applicazione](#applicazione)
  - [Struttura del codice](#struttura-del-codice)
  - [Tests](#tests)

# **Installazione**

L'installazione di questo progetto richiede 3 passaggi totali (+1 se si vuole sviluppare in locale) che devono essere eseguiti in sequenza. Se questi passaggi sono eseguiti correttamente, l'applicazione dovrebbe partire senza problemi. Altrimenti è molto probabile che si verifichino errori di vario tipo (moduli mancanti, chiavi API non trovate, ecc.).

1. Configurazioni dell'app e delle variabili d'ambiente
2. Installare Ollama e i modelli locali
3. Far partire il progetto con Docker (consigliato)
4. (Solo per sviluppo locale) Installare uv e creare l'ambiente virtuale

> [!IMPORTANT]\
> Prima di iniziare, assicurarsi di avere clonato il repository e di essere nella cartella principale del progetto.

### **1. Configurazioni**

Ci sono due file di configurazione principali che l'app utilizza: `configs.yaml` e `.env`.

#### **1.1 File di Configurazione dell'Applicazione**

Il file `configs.yaml` contiene le configurazioni generali dell'applicazione (modelli, strategie, provider API, ecc.) e deve essere creato localmente copiando il file di esempio:

```sh
cp configs.yaml.example configs.yaml
nano configs.yaml  # esempio di modifica del file
```

Il file `configs.yaml.example` include tutte le configurazioni disponibili con tutti i wrapper e modelli abilitati. Puoi personalizzare il tuo `configs.yaml` locale in base ai modelli che hai scaricato con Ollama e ai provider API che intendi utilizzare.

#### **1.2 Variabili d'Ambiente**

Per le variabili d'ambiente, bisogna copiare il file `.env.example` in `.env` e successivamente modificarlo con le tue API keys:
```sh
cp .env.example .env
nano .env  # esempio di modifica del file
```

Le API Keys devono essere inserite nelle variabili opportune dopo l'uguale e ***senza*** spazi. Esse si possono ottenere tramite i loro providers (alcune sono gratuite, altre a pagamento).\
Nel file [.env.example](.env.example) sono presenti tutte le variabili da compilare con anche il link per recuperare le chiavi, quindi, dopo aver copiato il file, basta seguire le istruzioni al suo interno.

Le chiavi non sono necessarie per far partire l'applicazione, ma senza di esse alcune funzionalità non saranno disponibili o saranno limitate. Per esempio senza la chiave di NewsAPI non si potranno recuperare le ultime notizie sul mercato delle criptovalute. Ciononostante, l'applicazione usa anche degli strumenti che non richiedono chiavi API, come Yahoo Finance e GNews, che permettono di avere comunque un'analisi di base del mercato.

> [!NOTE]\
> Entrambi i file `.env` e `configs.yaml` non vengono tracciati da git, quindi possono essere modificati liberamente.

### **2. Ollama**
Per utilizzare modelli AI localmente, è necessario installare Ollama, un gestore di modelli LLM che consente di eseguire modelli direttamente sul proprio hardware. Si consiglia di utilizzare Ollama con il supporto GPU per prestazioni ottimali, ma è possibile eseguirlo anche solo con la CPU.

Per l'installazione scaricare Ollama dal loro [sito ufficiale](https://ollama.com/download/linux).

Dopo l'installazione, si possono iniziare a scaricare i modelli desiderati tramite il comando `ollama pull <model>:<tag>`.

I modelli usati dall'applicazione sono quelli specificati nella sezione `models` del file di configurazione `configs.yaml` (ad esempio `models.ollama`). Se in locale si hanno dei modelli diversi, è possibile modificare il file `configs.yaml` per usare quelli disponibili.

I modelli consigliati per questo progetto sono:
- **Modelli leggeri** (per sviluppo/test): `qwen3:1.7b`, `phi4-mini:3.8b`  
- **Modelli bilanciati** (raccomandati): `qwen3:4b`, `qwen3:8b`
- **Modelli pesanti** (per prestazioni ottimali): `qwen3:14b`, `qwen3:32b`

Il sistema assegna automaticamente ruoli diversi ai modelli: Team Leader (modello principale), Team Members (agenti specializzati), Query Analyzer e Report Generator. È possibile configurare modelli diversi per ogni ruolo nel file `configs.yaml`.

### **3. Docker**
Se si vuole solamente avviare il progetto, si consiglia di utilizzare [Docker](https://www.docker.com), dato che sono stati creati i files [Dockerfile](Dockerfile) e [docker-compose.yaml](docker-compose.yaml) per creare il container con tutti i file necessari e già in esecuzione.

```sh
docker compose up --build -d
```

Se si sono seguiti i passaggi precedenti per la configurazione delle variabili d'ambiente, l'applicazione dovrebbe partire correttamente, dato che il file `.env` verrà automaticamente caricato nel container grazie alla configurazione in `docker-compose.yaml`.

### **4. UV (solo per sviluppo locale)**

Per prima cosa installa uv se non è già presente sul sistema

```sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Dopodiché bisogna creare un ambiente virtuale per lo sviluppo locale e impostare PYTHONPATH. Questo passaggio è necessario per far sì che Python riesca a trovare tutti i moduli del progetto e ad installare tutte le dipendenze. Fortunatamente uv semplifica molto questo processo:

```sh
uv venv
uv pip install -e .
```

A questo punto si può già modificare il codice e, quando necessario, far partire il progetto tramite il comando:

```sh
uv run src/app
```

# **Applicazione**

L'applicazione viene fatta partire tramite il file [src/app/\_\_main\_\_.py](src/app/__main__.py) che contiene il codice principale per l'inizializzazione e l'esecuzione del sistema di consulenza finanziaria basato su LLM Agents.

In esso viene creato il server Gradio per l'interfaccia web (porta predefinita 8000, configurabile in `configs.yaml`) e viene anche inizializzato il bot di Telegram (se è stata inserita la chiave nel file `.env` ottenuta da [BotFather](https://core.telegram.org/bots/features#creating-a-new-bot)).

L'utente può configurare inizialmente:
- **Modello AI**: Scegliere tra diversi provider (Ollama, OpenAI, Gemini, ecc.)
- **Strategia di investimento**: 
  - *Conservative*: Focus su investimenti stabili e a basso rischio
  - *Balanced*: Mix di crescita e stabilità  
  - *Aggressive*: Investimenti ad alto rischio e alto rendimento

L'interazione è guidata, sia tramite l'interfaccia web che tramite il bot di Telegram; l'utente può inviare un messaggio di testo libero per chiedere consigli o informazioni specifiche. Per esempio: "Qual è l'andamento attuale di Bitcoin?" o "Consigliami quali sono le migliori criptovalute in cui investire questo mese".

L'applicazione, una volta ricevuta la richiesta, procede a fare le seguenti operazioni:
1. **Query Check**: Analizza la richiesta dell'utente per controllare che la query sia valida e relativa alle criptovalute.
2. **Team Initialization**: Inizializza il Team di agenti coordinato da un Team Leader per l'analisi del mercato.
3. **Data Collection**: Ogni agente del Team recupera i dati necessari dalle API esterne se richiesto:
   - Dati di mercato (prezzi, volumi, capitalizzazione)
   - Notizie e sentiment
   - Discussioni sui social media
4. **Analysis & Synthesis**: Il Team Leader coordina gli agenti, recupera le risposte e genera una sintesi.
5. **Report Generation**: Un agente dedicato impagina la risposta finale in formato Markdown leggibile.
6. **Delivery**: La risposta viene inviata tramite l'interfaccia web o come allegato PDF dal bot di Telegram.

Gli agenti coinvolti in questo processo sono:
- **Query Check**: Verifica che la richiesta dell'utente sia valida e riguardi le criptovalute.
- **Team Leader**: Coordina gli agenti del team, gestisce la pipeline di esecuzione e fornisce una risposta finale basata sui dati raccolti.
- **Market Agent**: Membro del Team, recupera i dati di mercato delle criptovalute da provider multipli (Binance, Coinbase, CryptoCompare, Yahoo Finance).
- **News Agent**: Membro del Team, recupera le ultime notizie sul mercato delle criptovalute da provider multipli (NewsAPI, GoogleNews, CryptoPanic, DuckDuckGo).
- **Social Agent**: Membro del Team, recupera i dati dai social media (Reddit, X/Twitter, 4chan) per analizzare il sentiment del mercato.
- **Report Generator**: Si occupa di impaginare la risposta finale in un formato Markdown leggibile e comprensibile per l'utente.

L'interazione di questa applicazione con l'utente finisce nell'istante in cui viene inviata la risposta finale.
Se l'utente vuole fare una nuova richiesta, deve inviarla nuovamente tramite l'interfaccia web o il bot di Telegram.
Ogni richiesta viene trattata come una nuova sessione, senza memoria delle interazioni precedenti, questo per garantire che ogni analisi sia basata esclusivamente sui dati attuali del mercato, siccome questo è un requisito fondamentale per un sistema di consulenza finanziaria affidabile.

Per quanto riguarda Telegram, all'utente vengono inviati i risultati tramite allegati PDF che rimangono disponibili indefinitamente nella chat con il bot, permettendo di mantenere uno storico delle analisi passate.

## Struttura del codice

```
src
└── app
    ├── __main__.py      <-- Entry point dell'applicazione
    ├── config.py        <-- Configurazioni app e gestione modelli
    ├── agents           <-- Agenti, Team, prompts e pipeline
    │   ├── core.py      <-- Classi base per agenti e input
    │   ├── pipeline.py  <-- Orchestrazione workflow agenti
    │   └── prompts/     <-- Istruzioni per ogni tipo di agente
    ├── api              <-- Tutte le API esterne e wrapper
    │   ├── core         <-- Classi core per le API
    │   ├── markets      <-- Market data provider (Binance, Coinbase, ecc.)
    │   ├── news         <-- News data provider (NewsAPI, GoogleNews, ecc.)
    │   ├── social       <-- Social data provider (Reddit, X/Twitter, ecc.)
    │   └── tools        <-- Tools per agenti creati dalle API
    └── interface        <-- Interfacce utente (Gradio, Telegram)
```

### Caratteristiche Tecniche

- **Multi-Provider**: Ogni categoria (mercato, notizie, social) supporta provider multipli con fallback automatico
- **Aggregated Calls**: Possibilità di chiamare tutti i provider simultaneamente per dati più completi
- **Pipeline Events**: Sistema di logging dettagliato per tracciare l'esecuzione degli agenti
- **Configurazione Flessibile**: Modelli AI diversi per ruoli diversi (Team Leader vs Team Members)
- **Error Handling**: Gestione robusta degli errori con retry automatici

## Tests

Per eseguire i test, assicurati di aver configurato correttamente le variabili d'ambiente nel file `.env` come descritto sopra. Poi esegui il comando:
```sh
uv run pytest -v

# Oppure per test specifici
uv run pytest -v tests/api/test_binance.py
uv run pytest -v -k "test_news"

# Oppure usando i markers
uv run pytest -v -m api
uv run pytest -v -m "api and not slow"
```

