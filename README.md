# **Progetto di Esame: Agente di Pianificazione Viaggi Intelligente**
Questa è la repository per l'esame di Applicazioni Intelligenti che consiste in:
- Progetto per 2/3 del voto.
- Orale per 1/3 dei punti compreso da:
  - Presentazione (come se lo facessimo ad un cliente) di gruppo
  - Orale singolo con domande del corso (teoria e strumenti visti)

L'obiettivo di questo progetto è creare un sistema basato su **LLM Agents** e deve dimostrare la capacità di ragionare, adattarsi a eventi esterni e comunicare in modo intelligente.

Una prima idea è quella di fare un sistema che genera itinerari personalizzati e adattivi in base a vincoli e informazioni in tempo reale.

## Installazione
Per l'installazione si possono seguire i seguenti step per creare l'ambiente corretto o utilizzare un ambiente Docker già pronto:

**Ambiente**: Per prima cosa si deve creare un nuovo environment Python:
```sh
python -m venv .venv
```

**Attivare l'ambiente**: dobbiamo usare uno dei seguenti comandi, in base al fatto che siamo su Windows o Unix.\
*Nota*: nel caso Windows non faccia partire lo script per policy interne di sicurezza, bisogna far eseguire questo comando prima di attivare l'ambiente virtuale creato: ``` Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser ```

|Sistema Operativo|Comando|
|:---|:---|
|Unix| ``` source .venv/bin/activate ``` |
|Windows| ``` .venv/Scripts/activate ``` |
|Windows (PS)| ``` .venv/Scripts/Activate.ps1 ``` |

**Dipendenze**: Infine installiamo le dipendenze nell'ambiente appena creato:
```sh
python -m pip install -r requirements.txt
```

**Run**: Successivamente si può far partire il progetto tramite il comando:
```sh
python src/app.py
```

### Docker
Alternativamente, se si ha installato Docker, si può utilizzare il [Dockerfile](Dockerfile) e il [docker-compose.yaml](docker-compose.yaml) per creare il container con tutti i file necessari e già in esecuzione:
```sh
docker compose up -d
```

## Applicazione
TODO
