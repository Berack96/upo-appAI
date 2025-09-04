### **Progetto di Esame: Agente di Analisi e Consulenza Crypto/Scommesse**

#### **Obiettivo**

Creare un sistema di consulenza basato su **LLM Agents** che analizza dati di mercato in tempo reale per fornire raccomandazioni strategiche e motivate su criptovalute o scommesse sportive. L'obiettivo è dimostrare la capacità dell'agente di interpretare dati complessi, ragionare su di essi e presentare un'analisi comprensibile e razionale.

---

#### **1. Input Utente e Analisi Preliminare**

L'utente fornisce una richiesta di analisi che include:

* **Tipo di analisi:** Criptovalute o scommesse sportive.
* **Dettagli specifici:** Nome della criptovaluta (es. "Ethereum") o nome dell'evento sportivo (es. "Partita di calcio Juventus vs. Inter").
* **Fattori da considerare:** Intervallo di tempo (es. "prossime 24 ore"), infortuni, condizioni meteo.
* **Stile di approccio:** Stile di investimento (aggressivo, conservativo) o tipo di scommessa.

L'**Agente Orchestratore** riceve queste informazioni e le prepara per gli agenti successivi.

---

#### **2. Processo di Analisi e Acquisizione Dati**

Questo processo si basa sulla collaborazione di più agenti specializzati, in linea con l'approccio dei modelli di ragionamento.

* **Agente RicercatoreDati:** Recupera dati di trading da API di exchange (es. Binance) per le criptovalute, o da database di statistiche sportive per le scommesse.
* **Agente AnalistaSentiment:** Esegue l'analisi di news e post su forum e social media per valutare il sentiment del mercato o del pubblico, individuando trend ed emozioni che possono influenzare l'andamento.
* **Agente MotorePredittivo:** Combina i dati numerici e le analisi di sentiment per generare previsioni e strategie plausibili, come un  **modello di ragionamento trasparente** .

---

#### **3. Valutazione e Selezione Strategica**

L'**Agente Orchestratore** valuta le previsioni generate e, in base al suo ragionamento, seleziona le strategie più appropriate per l'utente.

* **Valutazione Logica:** Analizza i dati raccolti, come volumi di scambio o statistiche di gioco.
* **Analisi Integrata:** Scarta o modifica le strategie se i dati del sentiment o altri fattori esterni lo rendono necessario. Ad esempio, potrebbe consigliare di non puntare su una squadra anche se le statistiche sono a suo favore, a causa di un report di infortunio.

---

#### **4. Presentazione dei Risultati**

Infine, il sistema presenta all'utente le raccomandazioni strategiche.

* **Consulenza Dettagliata:** Ogni proposta include un riassunto della strategia, le ragioni che la supportano e i dati presi in considerazione.
* **Ragionamenti (Note):** Vengono aggiunte note esplicative che descrivono il processo decisionale degli agenti, dimostrando il "perché" di una certa scelta. Ad esempio: "Questa strategia è consigliata perché l'analisi del sentiment indica un forte interesse nella criptovaluta X, nonostante un recente calo di prezzo."
