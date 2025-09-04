### **Progetto di Esame: Agente di Pianificazione Corsi Intelligente**

#### **Obiettivo del Progetto**

Creare un sistema basato su **LLM Agents** capace di generare un piano didattico completo e personalizzato per un corso, a partire da input dell'utente. Il sistema dovrà dimostrare capacità di  **ragionamento** , **pianificazione adattiva** e **collaborazione tra agenti** per produrre output strutturati e coerenti.

---

### **1. Architettura del Sistema**

Il sistema è basato su un'architettura a  **due livelli** : una **UI** per l'input e un **sistema multi-agente** lato server per l'elaborazione.

* **Interfaccia Utente (UI)** : Frontend semplice e intuitivo che raccoglie i parametri del corso.
* **Input obbligatori** : Argomento del corso, ore totali, numero di lezioni.
* **Input opzionali** : Descrizione aggiuntiva, livello degli studenti (basso, medio, alto), generazione esercizi (toggle), parte pratica (toggle), upload di file (per libri, dispense, ecc.).
* **Motore di Ragionamento (Server)** : Core del sistema, dove agenti autonomi collaborano per produrre i materiali didattici.

---

### **2. Flusso di Lavoro e Ruolo degli Agenti**

Il processo si svolge in una sequenza di passaggi orchestrati dall' **Agente Principale** .

* **Agente `PianificatoreCorso` (Orchestratore)**

  * **Funzione** : Riceve tutti gli input dalla UI. È responsabile della coerenza e della coesione del progetto.

  1. **Validazione** : Valuta la coerenza degli input (es. se le ore totali corrispondono a `lezioni * ore_per_lezione`).
  2. **Ragionamento e Pianificazione** : Genera una bozza di piano del corso, suddividendo l'argomento principale in lezioni e argomenti secondari, bilanciando teoria e pratica in base alle richieste.
  3. **Orchestrazione Agenti** : Delega la creazione dei contenuti specifici (presentazioni, dispense, esercizi) agli agenti specializzati, fornendo loro gli input necessari.
* **Agente `GeneratoreContenuti` (Collaboratore)**

  * **Funzione** : Crea i documenti testuali per le dispense e le note del relatore per ogni lezione.
  * **Input** : Argomenti specifici per la lezione, livello degli studenti.
  * **Tool** : Utilizza un LLM (es. `Ollama` o API `OpenAI`) per la generazione di testo dettagliato.
  * **Output** : Un file `.md` o `.txt` per ogni lezione.
* **Agente `GeneratorePresentazioni` (Collaboratore)**

  * **Funzione** : Realizza le presentazioni `.pptx` per ogni lezione, basandosi sul contenuto generato e su un tema predefinito.
  * **Input** : Punti chiave e testo delle slide per ogni argomento, tema grafico.
  * **Tool** : Combina un LLM per la generazione del testo delle slide con la libreria **`python-pptx`** per la creazione del file.
  * **Output** : Un file `.pptx` per ogni lezione.
* **Agente `GeneratoreEsercizi` (Collaboratore, Opzionale)**

  * **Funzione** : Crea esercizi pratici a partire dagli argomenti teorici, in base al livello degli studenti.
  * **Input** : Argomenti specifici, tipo di corso (pratico/teorico), livello.
  * **Tool** : Utilizza un LLM per descrivere gli esercizi in formato testuale.
  * **Output** : Un file di testo con la descrizione degli esercizi per ogni lezione.
* **Agente `RicercatoreWeb` (Collaboratore, Opzionale)**

  * **Funzione** : Convalida e arricchisce il piano del corso con informazioni aggiornate o conferme sugli argomenti.
  * **Input** : Argomenti del corso.
  * **Tool** : Utilizza uno strumento di ricerca web (ad esempio, un'API di ricerca) per trovare riferimenti o dati aggiuntivi.
  * **Output** : Dati di supporto da passare agli altri agenti.

---

### **3. Output Finale**

Una volta che tutti gli agenti hanno completato i loro compiti, il programma finale raccoglie i documenti prodotti (`.md`, `.txt`, `.pptx`). L'output sarà una **cartella compressa (`.zip`)** che conterrà tutti i materiali, organizzati per lezione (es. `Lezione_1_Intro_Python/`, `Lezione_2_Variabili/`). Questa struttura permette all'utente di avere subito un pacchetto pronto all'uso.
