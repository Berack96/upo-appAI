# Utilizziamo Debian slim invece di Alpine per migliore compatibilità
FROM debian:bookworm-slim

# Installiamo le dipendenze di sistema
RUN apt-get update && \
    apt-get install -y curl npm && \
    rm -rf /var/lib/apt/lists/*
RUN npm install -g rettiwt-api

# Installiamo uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Configuriamo UV per usare copy mode ed evitare problemi di linking
ENV UV_LINK_MODE=copy

# Creiamo l'ambiente virtuale con tutto già presente
COPY pyproject.toml ./
COPY uv.lock ./
RUN uv sync --frozen --no-dev
ENV PYTHONPATH="./src"

# Copiamo i file del progetto
COPY LICENSE ./
COPY src/ ./src/
COPY configs.yaml ./

# Comando di avvio dell'applicazione
CMD ["uv", "run", "src/app"]
