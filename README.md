# **Agente di Analisi e Consulenza Crypto**
Questa è la repository per l'esame di Applicazioni Intelligenti che consiste in:
- Progetto per 2/3 del voto.
- Orale per 1/3 dei punti composto da:
  - Presentazione (come se lo facessimo ad un cliente) di gruppo
  - Orale singolo con domande del corso (teoria e strumenti visti)

L'obiettivo è quello di creare un sistema di consulenza finanziaria basato su LLM Agents che analizza il mercato delle criptovalute per fornire consigli di investimento personalizzati. Inoltre il sistema deve dimostrare la capacità di ragionare, gestire la persistenza dei dati, utilizzare fonti esterne e presentare un'analisi comprensibile e razionale, offrendo sia una consulenza ad ampio spettro che su una singola criptovaluta.

# **Indice**
- [Installazione](#installazione)
  - [1. Variabili d'Ambiente](#1-variabili-dambiente)
  - [2. Ollama](#2-ollama)
  - [3. Docker](#3-docker)
  - [4. UV (solo per sviluppo locale)](#4-uv-solo-per-sviluppo-locale)
- [Applicazione](#applicazione)
  - [Struttura del codice del Progetto](#struttura-del-codice-del-progetto)
  - [Tests](#tests)

# **Installazione**

L'installazione di questo progetto richiede 3 passaggi totali (+1 se si vuole sviluppare in locale) che devono essere eseguiti in sequenza. Se questi passaggi sono eseguiti correttamente, l'applicazione dovrebbe partire senza problemi. Altrimenti è molto probabile che si verifichino errori di vario tipo (moduli mancanti, chiavi API non trovate, ecc.).

1. Configurare le variabili d'ambiente
2. Installare Ollama e i modelli locali
3. Far partire il progetto con Docker (consigliato)
4. (Solo per sviluppo locale) Installare uv e creare l'ambiente virtuale

> [!IMPORTANT]\
> Prima di iniziare, assicurarsi di avere clonato il repository e di essere nella cartella principale del progetto.

### **1. Variabili d'Ambiente**

Copia il file `.env.example` in `.env` e successivamente modificalo con le tue API keys:
```sh
cp .env.example .env
nano .env  # esempio di modifica del file
```

Le API Keys devono essere inserite nelle variabili opportune dopo l'uguale e ***senza*** spazi. Esse si possono ottenere tramite i loro providers (alcune sono gratuite, altre a pagamento).\
Nel file [.env.example](.env.example) sono presenti tutte le variabili da compilare con anche il link per recuperare le chiavi, quindi, dopo aver copiato il file, basta seguire le istruzioni al suo interno.

Le chiavi non sono necessarie per far partire l'applicazione, ma senza di esse alcune funzionalità non saranno disponibili o saranno limitate. Per esempio senza la chiave di NewsAPI non si potranno recuperare le ultime notizie sul mercato delle criptovalute. Ciononostante, l'applicazione usa anche degli strumenti che non richiedono chiavi API, come Yahoo Finance e GNews, che permettono di avere comunque un'analisi di base del mercato.

### **2. Ollama**
Per utilizzare modelli AI localmente, è necessario installare Ollama, un gestore di modelli LLM che consente di eseguire modelli direttamente sul proprio hardware. Si consiglia di utilizzare Ollama con il supporto GPU per prestazioni ottimali, ma è possibile eseguirlo anche solo con la CPU.

Per l'installazione scaricare Ollama dal loro [sito ufficiale](https://ollama.com/download/linux).

Dopo l'installazione, si possono iniziare a scaricare i modelli desiderati tramite il comando `ollama pull <model>:<tag>`.

I modelli usati dall'applicazione sono visibili in [src/app/models.py](src/app/models.py). Di seguito metto lo stesso una lista di modelli, ma potrebbe non essere aggiornata:
- `gpt-oss:latest`
- `qwen3:latest`
- `qwen3:4b`
- `qwen3:1.7b`

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
uv run python src/app
```

# **Applicazione**

***L'applicazione è attualmente in fase di sviluppo.***

Usando la libreria ``gradio`` è stata creata un'interfaccia web semplice per interagire con l'agente principale. Gli agenti secondari si trovano nella cartella `src/app/agents` e sono:
- **Market Agent**: Agente unificato che supporta multiple fonti di dati con auto-retry e gestione degli errori.
- **News Agent**: Recupera le notizie finanziarie più recenti sul mercato delle criptovalute.
- **Social Agent**: Analizza i sentimenti sui social media riguardo alle criptovalute.
- **Predictor Agent**: Utilizza i dati raccolti dagli altri agenti per fare previsioni.

Si può accedere all'interfaccia anche tramite un Bot di Telegram se si inserisce la chiave ottenuta da [BotFather](https://core.telegram.org/bots/features#creating-a-new-bot).

## Struttura del codice del Progetto

```
src
└── app
    ├── __main__.py
    ├── agents       <-- Agenti, modelli, prompts e simili
    ├── base         <-- Classi base per le API
    ├── markets      <-- Market data provider (Es. Binance)
    ├── news         <-- News data provider (Es. NewsAPI)
    ├── social       <-- Social data provider (Es. Reddit)
    └── utils        <-- Codice di utilità generale
```

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

