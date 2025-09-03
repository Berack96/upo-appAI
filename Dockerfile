# Per ora abbiamo bisogno solo di python, se nel futuro avremo bisogno di pytorch/cuda possiamo sempre tornare indietro
#FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel
FROM python:3.11-slim

# Copio tutti i dati del progetto nella workdir
# (dopo aver definito la workdir mi trovo già in essa)
WORKDIR /app
COPY src .
COPY requirements.txt .
COPY LICENSE .

# Installo le dipendenze
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "src/app.py"]
