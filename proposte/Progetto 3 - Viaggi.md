### **Progetto di Esame: Agente di Pianificazione Viaggi Intelligente**

#### **Obiettivo**

Creare un sistema di pianificazione viaggi basato su **LLM Agents** che genera itinerari personalizzati e adattivi in base a vincoli e informazioni in tempo reale. L'obiettivo è dimostrare la capacità del sistema di ragionare, adattarsi a eventi esterni e comunicare in modo intelligente.

---

#### **1. Input Utente e Analisi Preliminare**

L'utente interagisce con una semplice interfaccia, fornendo una richiesta di viaggio che include:

* **Vincoli finanziari:** Budget massimo.
* **Preferenze di viaggio:** Tipologia di vacanza (es. mare, montagna, città) e mezzo di trasporto preferito (es. treno, aereo).
* **Tempistiche:** Date di viaggio e durata.

L'**Agente di Comunicazione** riceve queste informazioni e, usando un **LLM**, le interpreta e le formatta per gli agenti successivi.

---

#### **2. Processo di Pianificazione e Acquisizione Dati**

Questo processo si basa sulla collaborazione di più agenti specializzati, in linea con l'approccio dei modelli di ragionamento.

* **Agente Pianificatore:** Sulla base della richiesta iniziale, questo agente genera internamente una serie di **idee di viaggio** iniziali.
* **Agente Meteo:** Per ogni destinazione, richiede le previsioni del tempo tramite un'API REST, come quella di `open-meteo.com` e `openstreetmap.org`.
* **Agente Notizie:** Interroga un'API di notizie (`newsapi.com`) per rilevare eventuali eventi imprevisti o avvisi importanti per le località considerate.
* **Agente Ricerca:** Per ogni idea di viaggio, raccoglie informazioni essenziali sui **punti di interesse**, sfruttando un database statico o un'API semplificata, come suggerito nelle linee guida del progetto.
* **Agente Logistico:** Ottiene dati simulati su opzioni di viaggio (voli, treni) e costi per ciascuna destinazione o da una API esterna (`serpapi.com/google-flights-api`)

---

#### **3. Valutazione e Selezione Adattiva**

L'**Agente Pianificatore** valuta le idee di viaggio in base alle informazioni raccolte dagli altri agenti.

* **Valutazione Logica:** Analizza il budget e la compatibilità dei mezzi di trasporto.
* **Adattabilità:** Scarta o modifica le proposte se le condizioni esterne lo rendono necessario. Ad esempio, non proporrà un viaggio al mare se sono previste forti piogge, o cambierà l'ordine delle tappe in base a notizie rilevanti.

---

#### **4. Presentazione dei Risultati**

Infine, il sistema presenta all'utente un massimo di tre proposte di viaggio.

* **Itinerari Dettagliati:** Ogni proposta include un riepilogo del viaggio, le tappe suggerite e i costi stimati.
* **Ragionamenti (Note):** Vengono aggiunte note esplicative che descrivono il processo decisionale degli agenti, dimostrando il "perché" della scelta fatta. Ad esempio, "Abbiamo evitato la città A perché le notizie riportano un evento di traffico locale".
