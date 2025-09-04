# **Progetto di Esame: Da definire**
Questa è la repository per l'esame di Applicazioni Intelligenti che consiste in:
- Progetto per 2/3 del voto.
- Orale per 1/3 dei punti composto da:
  - Presentazione (come se lo facessimo ad un cliente) di gruppo
  - Orale singolo con domande del corso (teoria e strumenti visti)

L'obiettivo di questo progetto è creare un sistema basato su **LLM Agents** e deve dimostrare la capacità di ragionare, adattarsi a eventi esterni e comunicare in modo intelligente.

# Installazione
Per l'installazione si può utilizzare un approccio tramite **uv** (manuale) oppure utilizzare un ambiente **Docker** già pronto (automatico)

### UV
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

### Docker
Alternativamente, se si ha installato [Docker](https://www.docker.com), si può utilizzare il [Dockerfile](Dockerfile) e il [docker-compose.yaml](docker-compose.yaml) per creare il container con tutti i file necessari e già in esecuzione:
```sh
docker compose up --build -d
```

# Applicazione
L'applicazione è attualmente in fase di sviluppo. Maggiori dettagli saranno aggiunti durante l'implementazione.
