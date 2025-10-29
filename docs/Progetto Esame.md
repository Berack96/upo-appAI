# Agente di Analisi e Consulenza Crypto

L'obiettivo è quello di creare un sistema di consulenza finanziaria basato su LLM Agents che analizza il mercato delle criptovalute per fornire consigli di investimento personalizzati. Inoltre il sistema deve dimostrare la capacità di ragionare, gestire la persistenza dei dati, utilizzare fonti esterne e presentare un'analisi comprensibile e razionale, offrendo sia una consulenza ad ampio spettro che su una singola criptovaluta.

## Input Utente e Personalizzazione

L'utente interagisce con una semplice interfaccia per fornire una richiesta di analisi. L'agente integra la memoria utente per fornire un'esperienza personalizzata e continuativa.

* **Tipologia di richiesta**: Analisi ad ampio spettro per un portafoglio diversificato o analisi specifica di una singola criptovaluta.
* **Dettagli specifici**: Stile di investimento (aggressivo o conservativo).
* **Fattori da considerare**: Intervallo di tempo dell'analisi (es. "prossime 24 ore") e, se richiesto, il nome della criptovaluta da analizzare.
* **Memoria**: L'Agente Orchestratore recupera la cronologia delle richieste passate dell'utente per fornire una consulenza che tenga conto delle scelte precedenti.

## Processo di Analisi e Acquisizione Dati

Questo processo si basa sulla collaborazione di più agenti specializzati, in linea con l'approccio dei modelli di ragionamento.

* Agente `RicercatoreDati`: Accede ad API di exchange (come [Binance](https://www.binance.com/it/binance-api), [Coindesk](https://developers.coindesk.com/documentation/data-api/introduction) o [ConMarketCap](https://coinmarketcap.com/api/documentation/v1/)) per recuperare i dati di trading (prezzo, volume, capitalizzazione di mercato) di un vasto set di criptovalute.
* Agente `AnalistaSentiment`: Questo agente opera su due fronti, analizzando dati non strutturati per valutare il sentimento del mercato:
* Agente `Social`: Esegue lo scraping di forum (es. Reddit) e social media (es. Twitter/X) per analizzare il sentiment del pubblico.
* Agente `News`: Interroga API di notizie (es. [NewsAPI](https://newsapi.org)) per individuare informazioni rilevanti (es. annunci di partnership, nuovi regolamenti) che potrebbero influenzare il mercato.
* Agente `MotorePredittivo`: Utilizza i dati numerici e le analisi di sentiment per generare previsioni e strategie plausibili per ogni criptovaluta analizzata, in linea con un modello di ragionamento trasparente.

## Valutazione e Selezione Strategica

L'Agente `Orchestratore` valuta le previsioni generate e, basandosi sul suo ragionamento e sulle preferenze dell'utente, seleziona le strategie più appropriate.

* **Valutazione Logica**: L'agente analizza i dati raccolti per identificare le criptovalute più sicure per un utente conservativo (es. alta capitalizzazione, bassa volatilità) o quelle con un alto potenziale di crescita per un utente aggressivo.
* **Analisi Integrata**: L'agente scarta o modifica le strategie se l'analisi del sentiment indica che sono presenti fattori di rischio non evidenti dai soli dati di mercato.

## Presentazione dei Risultati e Persistenza

Infine, il sistema presenta all'utente un riepilogo dettagliato di tutte le raccomandazioni e salva la sessione per un futuro utilizzo.

* **Consulenza Dettagliata**: La proposta include una serie di possibili investimenti. Per ogni criptovaluta suggerita, il sistema indica la percentuale di portafoglio da investire, la durata consigliata dell'investimento e le ragioni che supportano la scelta.
* **Ragionamenti (Note)**: Vengono aggiunte note esplicative che descrivono il processo decisionale degli agenti, dimostrando il "perché" di una certa scelta.
* **Persistenza Utente**: Tutti i dati della sessione vengono salvati in un database, permettendo all'utente di richiedere una nuova consulenza in futuro per valutare l'andamento del portafoglio e la validità delle scelte fatte.