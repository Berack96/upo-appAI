# Utilizziamo Debian slim invece di Alpine per migliore compatibilità
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Installiamo uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Configuriamo UV per usare copy mode ed evitare problemi di linking
ENV UV_LINK_MODE=copy

# Impostiamo la directory di lavoro
WORKDIR /app

# Copiamo i file del progetto
COPY pyproject.toml ./
COPY uv.lock ./
COPY LICENSE ./
COPY src/ ./src/
COPY configs.yaml ./

# Creiamo l'ambiente virtuale con tutto già presente
RUN uv sync
ENV PYTHONPATH="/app/src"

# Comando di avvio dell'applicazione
CMD ["uv", "run", "src/app"]
