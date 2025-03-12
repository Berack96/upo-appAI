### Passo 0: Gestire Windows
La natura di questa guida è permettere agli utenti Windows di lavorare con Docker e con la GPU nei progetti pytorch (similarmente tensorflow). Rispettare questi passi, possibilmente in ordine:
1. Installare i driver aggiornati della propria GPU Nvidia
2. Installare [Nvidia Toolkit](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local) dal sito ufficiale Nvidia.
	1. Se tutto va a buon fine lanciare in Powershell il comando `nvidia-smi` e dovrebbe comparire un output simile a questo:
	   
```bash
	  Fri Mar  7 13:57:22 2025
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.124.03             Driver Version: 572.60         CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4090        On  |   00000000:0C:00.0  On |                  Off |
| 31%   57C    P2            312W /  450W |   14791MiB /  24564MiB |     91%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

3. Windows mantiene la compatibilità con i vari tool e framework appoggiandosi a WSL2, ossia la virtualizzazione integrata di Linux. È quindi necessario avere l'opzione di virtualizzazione abilitata nel proprio BIOS del computer. Se WSL2 si apre significa che è già attiva e non devi fare niente. Si consiglia una versione Ubuntu ma non dovrebbero esserci problemi con altre distro. 
4. WSL2 permette il pass through della GPU solo installando nella distro WSL2 scelta le dipendenze necessarie come indicato [sul sito Nvidia](https://docs.nvidia.com/cuda/wsl-user-guide/index.html). Anche da WSL2 lanciare il comando `nvidia-smi` e aspettarsi un output simile al precedente.
5. Installare Docker su Windows e nelle impostazioni sotto al tab `Generale` controllare che sia abilitato l'uso di WSL2. Oramai di default è abilitato ma per scrupolo controllare.
### Passo 1: Creare un file Dockerfile

1. **Crea il Dockerfile**: All'interno della tua directory del progetto, crea un file chiamato `Dockerfile`. (Sì, senza estensione)
    
2. **Contenuto del Dockerfile**:
```dockerfile 
# Usa l'immagine base di PyTorch con supporto per CUDA 12.6 e CuDNN 9
FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel

# Imposta il working directory all'interno del container
WORKDIR /upo-appAI

# Copia i file necessari nel container
COPY requirements.txt .

# Installa le dipendenze Python dalla lista in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia i file del progetto all'interno del container
COPY . /upo-appAI
```

### Passo 2: Costruire l'immagine Docker

1. **Costruisci l'immagine**: Apri un terminale e naviga alla directory `upo-appAI`. Esegui il seguente comando per costruire l'immagine Docker:
```bash
docker build -t appAI .
```
Da questo momento l'immagine avrà il nome di `appAI`
### Passo 3: Creare e gestire un container
Per il momento ci occuperemo di crearne uno ma se serve agganciarlo ad un IDE l'operazione potrebbe richiedere configurazioni specifiche per il singolo IDE. Ad esempio Pycharm di Jetbrains crea un nuovo container a partire dalla immagine compilata o addirittura direttamente dal dockerfile, quindi se interessa Pycharm saltare al punto che lo tratta senza creare il container come indicato qui sotto, anche se raccomandato leggerlo per conoscenza.

**Avvia il container**: Una volta che l'immagine è stata costruita, puoi avviare un container con il comando che segue avendo cura di essere nel percorso della cartella di progetto:
```bash 
docker run --name appAI_container --gpus all -v ${PWD}:/upo-appAI -it appAI /bin/sh
```
Questo comando monta la directory corrente sul volume del container e ti dà accesso a una shell interattiva. Attenzione:
* In PowerShell, la sintassi corretta per ottenere il percorso corrente è `${PWD}` mentre su shell Linux sarebbe `$(pwd)`, se capita di usare comandi suggeriti da vari LLM prestarci attenzione.
* Si può sostituire col percorso assoluto della cartella di progetto.

È importante il `--gpus all` altrimenti CUDA non funziona. Sostituire `all` con il nome della GPU nel caso ce ne sia più di una e non interessa usarle tutte. 
Per scrupolo, controlliamo che funzioni tutto bene nel container lanciando il comando nella shell del cocker appena avviato:
```shell
python -c "import torch; print(torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```
Ci si aspetta questo output:
```bash
2.6.0+cu126
CUDA available: True
```

Una alternativa è lanciare il comando `nvidia-smi` aspettandosi come output qualcosa di molto simile a quanto visto sopra.

Per accedere in un secondo momento alla shell del Docker usare il comando:
```shell 
docker exec -it appAI_container /bin/sh
``` 


#### Manipolazione Generale
Per gestire i container docker si può passare da GUI (Windows) o da CLI ma in entrambi i casi i container non possono essere modificati runtime. 

##### Rimozione container
O da GUI usando i 3 puntini verticali sul nome del container, o da CLI coi comandi 
```shell
docker stop appAI_container # STOP del docker prima della rimozione
docker rm appAI_container # Eliminazione effettiva del contenitore
```

##### Riavvio Container
Sempre o da GUI o col comando:
```bash
docker restart appAI_container
```

#### Pycharm
Premessa: pycharm non si aggancia ad un container esistente di default quindi o si crea una connessione di rete (anche locale) oppure pycharm ha bisogno di creare il suo. Per ragioni di comodità si sceglie di lasciar creare un nuovo container a pycharm. 
Per usare docker come python interpreter bisogna aggiungerne un nuovo interprete e selezionare docker. Qui si può scegliere se selezionare l'immagine già compilata o partire dal Dockerfile. Attenzione!!! Qui non è possibile specificare il `--gpus all` e andrà fatto dopo la creazione del Docker. Una volta finito andare nelle opzioni di esecuzione in `Edit Configurations` tirando giù il menu a tendina di fianco al bottone play in alto a destra. 

<img src="Configurazione Ambiente di Lavoro - Run and Debug config.png" alt="Configurazione Ambiente di Lavoro - Edit Docker Container Settings" width="650" style="display: block; margin: auto;" />

In `docker container setting` fare click sul simbolo della cartella. Si aprirà una finestra in cui in fondo bisogna inserire dentro a `Run options` l'opzione `--gpus all`.

<img src="Configurazione Ambiente di Lavoro - Edit Docker Container Settings.png" alt="Configurazione Ambiente di Lavoro - Edit Docker Container Settings" width="650" style="display: block; margin: auto;" />

