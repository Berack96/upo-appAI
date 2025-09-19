# **Progetto di Esame: Da definire**
Questa è la repository per l'esame di Applicazioni Intelligenti che consiste in:
- Progetto per 2/3 del voto.
- Orale per 1/3 dei punti composto da:
  - Presentazione (come se lo facessimo ad un cliente) di gruppo
  - Orale singolo con domande del corso (teoria e strumenti visti)

L'obiettivo di questo progetto è creare un sistema basato su **LLM Agents** e deve dimostrare la capacità di ragionare, adattarsi a eventi esterni e comunicare in modo intelligente.

# Installazione
Per l'installazione si può utilizzare un approccio tramite **uv** (manuale) oppure utilizzare un ambiente **Docker** già pronto (automatico).

Prima di avviare l'applicazione è però necessario configurare correttamente le API keys e installare Ollama per l'utilizzo dei modelli locali, altrimenti il progetto, anche se installato correttamente, non riuscirà a partire.

### API Keys
Le API Keys puoi ottenerle tramite i seguenti servizi:
- **Google AI**: [Google AI Studio](https://makersuite.google.com/app/apikey) (gratuito con limiti)
- **Anthropic**: [Anthropic Console](https://console.anthropic.com/)
- **DeepSeek**: [DeepSeek Platform](https://platform.deepseek.com/)
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/api-keys)

Nota che alcune API sono gratuite con limiti di utilizzo, altre sono a pagamento. Google offre attualmente l'accesso gratuito con limiti ragionevoli.

### Ollama (Modelli Locali)
Per utilizzare modelli AI localmente, è necessario installare Ollama:

**1. Installazione Ollama**:
- **Linux**: 
```sh 
curl -fsSL https://ollama.com/install.sh | sh
```
- **macOS/Windows**: Scarica l'installer da [https://ollama.com/download/windows](https://ollama.com/download/windows)

**2. GPU Support (Raccomandato)**:
Per utilizzare la GPU con Ollama, assicurati di avere NVIDIA CUDA Toolkit installato:
- **Download**: [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local)
- **Documentazione WSL**: [CUDA WSL User Guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

**3. Installazione Modelli**:
Si possono avere più modelli installati contemporaneamente. Per questo progetto si consiglia di utilizzare il modello open source `gpt-oss` poiché prestante e compatibile con tante funzionalità. Per il download:
```sh 
ollama pull gpt-oss:latest
```

### Variabili d'Ambiente

**1. Copia il file di esempio**:
```sh
cp .env.example .env
```

**2. Modifica il file .env** creato con le tue API keys e il path dei modelli Ollama, inserendoli nelle variabili opportune dopo l'uguale e ***senza*** spazi:
```dotenv
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
OPENAI_API_KEY=
# Path dove Ollama salva i modelli (es. /home/username/.ollama su Linux)
OLLAMA_MODELS_PATH=
```

### Opzione 1 UV
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

### Opzione 2 Docker
Alternativamente, se si ha installato [Docker](https://www.docker.com), si può utilizzare il [Dockerfile](Dockerfile) e il [docker-compose.yaml](docker-compose.yaml) per creare il container con tutti i file necessari e già in esecuzione:

**IMPORTANTE**: Assicurati di aver configurato il file `.env` come descritto sopra prima di avviare Docker.

```sh
docker compose up --build -d
```

Il file `.env` verrà automaticamente caricato nel container grazie alla configurazione in `docker-compose.yaml`.

# Applicazione
**L'applicazione è attualmente in fase di sviluppo.** 
## Aggiornamento del 19 Giugno 2024
Usando la libreria ``gradio`` è stata creata un'interfaccia web semplice per interagire con gli agenti. Gli agenti si trovano
nella cartella `src/app/agents` e sono:
- **Market Agent**: Recupera i dati di mercato (prezzi, volumi, ecc.). ***MOCK***
- **News Agent**: Recupera le notizie finanziarie più recenti utilizzando. ***MOCK***
- **Social Agent**: Analizza i sentimenti sui social media utilizzando. ***MOCK***
- **Predictor Agent**: Utilizza i dati raccolti dagli altri agenti per fare previsioni.

L'applicazione principale si trova in `src/app.py` e può essere eseguita con il comando:
```sh
uv run python src/app.py
```

### Albero delle cartelle:
```txt
upo-appAI/
├── Dockerfile
├── LICENSE
├── README.md
├── docker-compose.yaml
├── docs/
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── __pycache__/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__/
│   │   │   ├── market_agent.py
│   │   │   ├── news_agent.py
│   │   │   ├── predictor_agent.py
│   │   │   └── social_agent.py
│   │   └── tool.py
│   ├── app.py
│   ├── example.py
│   └── ollama_demo.py
└── uv.lock
```

### Problemi noti
1. Google ci sono differenze fra i modelli 1.x e i modelli 2.x. Si suggerisce la costruzione di due metodi differenti. 
   2. `gemini-1.5-flash` funziona perfettamente
   3. `gemini-2.5-flash` non funziona passando parametri come *temperature* e *max_tokens*, bisogna trovare la nuova sintassi.
2. Ollama viene correttamente triggerato dalla selezione da interfaccia web ma la generazione della risposta non viene parsificata correttamente. 

### ToDo
1. Per lo scraping online bisogna iscriversi e recuperare le chiavi API
   2. **Market Agent**: [CoinGecko](https://www.coingecko.com/it)
   3. **News Agent**: [CryptoPanic](https://cryptopanic.com/)
   4. **Social Agent**: [post più hot da r/CryptoCurrency (Reddit)](https://www.reddit.com/)
5. Capire come `gpt-oss` parsifica la risposta e per questioni "estetiche" si può pensare di visualizzare lo stream dei token. Vedere il sorgente `src/ollama_demo.py` per risolvere il problema.