# Utilizziamo Debian slim invece di Alpine per migliore compatibilità
FROM debian:bookworm-slim

# Installiamo le dipendenze di sistema
RUN apt update && \
    apt install -y curl && \
    rm -rf /var/lib/apt/lists/*

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

# Installiamo le dipendenze per X (rettiwt, nodejs e npm)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
RUN apt install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN npm install -g rettiwt-api

# Copiamo i file del progetto
COPY LICENSE ./
COPY src/ ./src/
COPY configs.yaml ./

# Comando di avvio dell'applicazione
CMD ["uv", "run", "src/app"]
