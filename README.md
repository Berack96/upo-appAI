# **Agente di Analisi e Consulenza Crypto**
Questa è la repository per l'esame di Applicazioni Intelligenti che consiste in:
- Progetto per 2/3 del voto.
- Orale per 1/3 dei punti composto da:
  - Presentazione (come se lo facessimo ad un cliente) di gruppo
  - Orale singolo con domande del corso (teoria e strumenti visti)

L'obiettivo è quello di creare un sistema di consulenza finanziaria basato su LLM Agents che analizza il mercato delle criptovalute per fornire consigli di investimento personalizzati. Inoltre il sistema deve dimostrare la capacità di ragionare, gestire la persistenza dei dati, utilizzare fonti esterne e presentare un'analisi comprensibile e razionale, offrendo sia una consulenza ad ampio spettro che su una singola criptovaluta.

# **Indice**
- [Installazione](#installazione)
  - [Ollama (Modelli Locali)](#ollama-modelli-locali)
  - [Variabili d'Ambiente](#variabili-dambiente)
  - [Installazione in locale con UV](#installazione-in-locale-con-uv)
  - [Installazione con Docker](#installazione-con-docker)
- [Applicazione](#applicazione)
   - [Ultimo Aggiornamento](#ultimo-aggiornamento)
   - [Tests](#tests)

# **Installazione**
Per l'installazione di questo progetto si consiglia di utilizzare **Docker**. Con questo approccio si evita di dover installare manualmente tutte le dipendenze e si può eseguire il progetto in un ambiente isolato.

Per lo sviluppo locale si può utilizzare **uv** che si occupa di creare un ambiente virtuale e installare tutte le dipendenze.

In ogni caso, ***prima*** di avviare l'applicazione è però necessario configurare correttamente le **API keys** e installare Ollama per l'utilizzo dei modelli locali, altrimenti il progetto, anche se installato correttamente, non riuscirà a partire.

### Ollama (Modelli Locali)
Per utilizzare modelli AI localmente, è necessario installare Ollama:

**1. Installazione Ollama**:
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`
- **macOS/Windows**: Scarica l'installer da [https://ollama.com/download/windows](https://ollama.com/download/windows)

**2. GPU Support (Raccomandato)**:
Per utilizzare la GPU con Ollama, assicurati di avere NVIDIA CUDA Toolkit installato:
- **Download**: [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local)
- **Documentazione WSL**: [CUDA WSL User Guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

**3. Installazione Modelli**:
Si possono avere più modelli installati contemporaneamente. Per questo progetto si consiglia di utilizzare il modello open source `gpt-oss` poiché prestante e compatibile con tante funzionalità. Per il download: `ollama pull gpt-oss:latest`

### Variabili d'Ambiente

**1. Copia il file di esempio**:
```sh
cp .env.example .env
```

**2. Modifica il file .env** creato con le tue API keys e il path dei modelli Ollama, inserendoli nelle variabili opportune dopo l'uguale e ***senza*** spazi.

Le API Keys puoi ottenerle tramite i seguenti servizi (alcune sono gratuite, altre a pagamento):
- **Google AI**: [Google AI Studio](https://makersuite.google.com/app/apikey) (gratuito con limiti)
- **Anthropic**: [Anthropic Console](https://console.anthropic.com/)
- **DeepSeek**: [DeepSeek Platform](https://platform.deepseek.com/)
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/api-keys)

## **Installazione in locale con UV**
**1. Installazione uv**: Per prima cosa installa uv se non è già presente sul sistema:
```sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Ambiente e dipendenze**: uv installerà python e creerà automaticamente l'ambiente virtuale con le dipendenze corrette:
```sh
uv sync --frozen --no-cache
```

**3. Run**: Successivamente si può far partire il progetto tramite il comando:
```sh
uv run python src/app.py
```

## **Installazione con Docker**
Alternativamente, se si ha installato [Docker](https://www.docker.com), si può utilizzare il [Dockerfile](Dockerfile) e il [docker-compose.yaml](docker-compose.yaml) per creare il container con tutti i file necessari e già in esecuzione:

**IMPORTANTE**: Assicurati di aver configurato il file `.env` come descritto sopra prima di avviare Docker.

```sh
docker compose up --build -d
```

Il file `.env` verrà automaticamente caricato nel container grazie alla configurazione in `docker-compose.yaml`.

# **Applicazione**

***L'applicazione è attualmente in fase di sviluppo.***

Usando la libreria ``gradio`` è stata creata un'interfaccia web semplice per interagire con l'agente principale. Gli agenti secondari si trovano nella cartella `src/app/agents` e sono:
- **Market Agent**: ~~Agente unificato che supporta multiple fonti di dati (Coinbase + CryptoCompare) con auto-configurazione~~  (non proprio un agente per ora)
- **News Agent**: Recupera le notizie finanziarie più recenti utilizzando. ***MOCK***
- **Social Agent**: Analizza i sentimenti sui social media utilizzando. ***MOCK***
- **Predictor Agent**: Utilizza i dati raccolti dagli altri agenti per fare previsioni.

## Ultimo Aggiornamento
### Market Agent Features:
- **Auto-configurazione**: Configura automaticamente i provider disponibili basandosi sulle env vars
- **Multiple provider**: Supporta sia Coinbase (trading) che CryptoCompare (market data)
- **Interfaccia unificata**: Un'unica API per accedere a tutti i provider

### Problemi con i modelli LLM:
1. **Ollama gpt-oss**: il modello `gpt-oss` funziona ma non riesce a seguire le istruzioni.
2. **Ollama-gwen**: il modello `gwen` funziona più veloce di `gpt-oss` ma comunque non segue le istruzioni.

### ToDo
1. [X] Per lo scraping online bisogna iscriversi e recuperare le chiavi API
2. [X] **Market Agent**: [CryptoCompare](https://www.cryptocompare.com/cryptopian/api-keys)
3. [X] **Market Agent**: [Coinbase](https://www.coinbase.com/cloud/discover/api-keys)
4. [] **News Agent**: [CryptoPanic](https://cryptopanic.com/)
5. [] **Social Agent**: [post più hot da r/CryptoCurrency (Reddit)](https://www.reddit.com/)
6. [] Capire come `gpt-oss` parsifica la risposta e per questioni "estetiche" si può pensare di visualizzare lo stream dei token. Vedere il sorgente `src/ollama_demo.py` per risolvere il problema.

## Tests

***Per ora ho cambiato tutto e quindi i test non funzionano***
