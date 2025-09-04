### **1. Proposta: Agente di Pianificazione Corsi Intelligente**

#### **Descrizione Dettagliata**

L'agente si concentra sulla generazione dinamica di programmi didattici completi e personalizzati. A differenza dei sistemi statici, questo progetto utilizza un'architettura multi-agente per ragionare sul contenuto, adattarsi a diversi livelli di competenza e produrre materiali didattici pronti all'uso. Il focus è sulla capacità del sistema di pianificare, generare e validare informazioni complesse, trasformando input semplici in una serie di documenti coerenti.

**Features Principali**

* **Pianificazione Adattiva** : Il sistema bilancia automaticamente gli argomenti teorici e pratici in base alle ore disponibili e al livello degli studenti.
* **Generazione di Contenuti Multipli** : Produce non solo il programma, ma anche dispense, presentazioni e note per il relatore, dimostrando la capacità di creare diversi tipi di output da un'unica fonte di dati.
* **Gestione di Dati Eterogenei** : Accetta input strutturati (ore, lezioni) e non strutturati (descrizioni, file di riferimento), dimostrando flessibilità.
* **Output Coerente** : Organizza tutti i materiali generati in una cartella compressa per una consegna facile e organizzata.

#### **Input Utente**

* **Argomento del corso** : Tema principale (es. "Introduzione a Python").
* **Ore totali** : Durata complessiva del corso.
* **Numero di lezioni** : Suddivisione del tempo.
* **Livello studenti** : Basso, medio o alto.
* **Opzioni Aggiuntive** : Toggle per esercizi e parte pratica, upload di file di riferimento.

#### **Agenti Lato Server**

* **Agente `PianificatoreCorso`** : L'orchestratore che riceve l'input, ragiona sulla struttura del corso e delega i compiti agli altri agenti.
* **Agente `GeneratoreDispense`** : Crea documenti testuali formattati per ogni lezione.
* **Agente `GeneratorePresentazioni`** : Genera file PowerPoint (.pptx) usando il contenuto fornito dall'LLM e la libreria `python-pptx`.
* **Agente `GeneratoreEsercizi`** : Produce esercizi pratici descritti testualmente, adattati al livello degli studenti.

---

### **2. Proposta: Agente di Analisi e Consulenza Crypto**

#### **Descrizione Dettagliata**

Il progetto crea un consulente virtuale che utilizza gli **LLM** per analizzare il mercato delle criptovalute. A differenza dei semplici tracker di prezzo, questo agente combina dati di mercato in tempo reale con l'analisi del sentiment online per fornire raccomandazioni strategiche e il ragionamento che le supporta. L'intelligenza del sistema risiede nella sua capacità di elaborare grandi quantità di dati non strutturati (news, social media) e di presentarli in una forma comprensibile e contestualizzata per l'utente.

**Features Principali**

* **Analisi in Tempo Reale** : Si connette a un'API per monitorare prezzi e volumi di scambio.
* **Sentiment Analysis** : Scansiona fonti online per rilevare il sentiment del mercato e i trend.
* **Consigli Strategici** : Non si limita a mostrare i dati, ma propone una strategia (es. "compra", "vendi", "hold") e ne spiega le motivazioni.
* **Ragionamento Trasparente** : Fornisce un resoconto dettagliato del processo decisionale, elencando i fattori che hanno portato a una specifica raccomandazione.

#### **Input Utente**

* **Nome della criptovaluta** : La moneta da analizzare (es. "Bitcoin", "Ethereum").
* **Intervallo di tempo** : Ore, giorni o settimane.
* **Stile di trading** : Aggressivo, conservativo.

#### **Agenti Lato Server**

* **Agente `RicercatoreMercato`** : Recupera dati di trading da API pubbliche.
* **Agente `AnalistaSentiment`** : Esegue lo scraping di notizie e post sui social per l'analisi del sentiment.
* **Agente `ConsulenteStrategico`** : Combina i dati raccolti, il sentiment e le preferenze dell'utente per formulare una strategia e le sue motivazioni.

---

### **3. Proposta: Agente di Pianificazione Viaggi Intelligente**

#### **Descrizione Dettagliata**

Questo progetto è un sistema che pianifica viaggi personalizzati e adattivi. L'agente intelligente non si limita a proporre un itinerario fisso, ma ragiona e modifica il piano in base a informazioni in tempo reale, dimostrando la sua capacità di adattamento a eventi imprevisti. La forza del progetto sta nel mostrare come un LLM può integrare dati da fonti eterogenee (meteo, notizie, punti di interesse) per prendere decisioni complesse e generare un output coerente e personalizzato.

**Features Principali**

* **Adattabilità in Tempo Reale** : Il piano di viaggio si adatta a variabili come le condizioni meteorologiche o gli eventi locali.
* **Pianificazione Basata su Dati** : Il sistema utilizza informazioni reali e simulazioni per ottimizzare il viaggio in base ai vincoli dell'utente e alle condizioni esterne.
* **Ragionamento Esplicito** : Spiega all'utente il "perché" di ogni decisione presa (es. "Abbiamo evitato la città A a causa di un evento locale imprevisto").
* **Output Organizzato** : Il risultato è un itinerario chiaro e dettagliato con tutte le informazioni necessarie per l'utente.

#### **Input Utente**

* **Vincoli finanziari** : Budget massimo.
* **Preferenze di viaggio** : Mare, montagna, città, ecc.
* **Tempistiche** : Date di viaggio e durata.

#### **Agenti Lato Server**

* **Agente `Pianificatore`** : L'orchestratore che crea l'itinerario e lo adatta in base alle informazioni degli altri agenti.
* **Agente `Meteo`** : Interroga un'API per le previsioni meteorologiche.
* **Agente `Notizie`** : Cerca eventi locali e notizie che potrebbero influenzare il viaggio.
* **Agente `Ricerca`** : Recupera informazioni sui punti di interesse, voli e treni da database o API.
