# Vogliamo usare una versione di linux leggera con già uv installato
# Infatti scegliamo l'immagine ufficiale di uv che ha già tutto configurato
# Nel caso in cui si volesse usare un'altra immagine di base che ha magari CUDA
# bisognerebbe installare uv manualmente come descritto nel README
#FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel   # Lo lascio qui nel caso
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Dopo aver definito la workdir mi trovo già in essa
WORKDIR /app

# Settiamo variabili d'ambiente per usare python del sistema invece che venv
ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV UV_LINK_MODE=copy

# Copiamo prima i file di configurazione delle dipendenze e installiamo le dipendenze
COPY pyproject.toml ./
COPY uv.lock ./
RUN uv sync --frozen --no-cache

# Copiamo i file sorgente dopo aver installato le dipendenze per sfruttare la cache di Docker
COPY LICENSE .
COPY src ./src

# Comando di default all'avvio dell'applicazione
CMD ["python", "src/app.py"]
