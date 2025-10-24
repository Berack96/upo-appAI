# Report Obsolescenza Documenti (docs/)

Valutazione dei documenti esistenti rispetto allo stato attuale del codice.

## Valutazione Documenti

- `App_Architecture_Diagrams.md`
  - Stato: parzialmente aggiornato.
  - Criticità: contiene sezioni su "Signers Architecture" (src/app/signers/…) che non esistono nel repo attuale; riferimenti a auto-detection provider non presenti esplicitamente nei wrappers (l’attuale gestione usa `WrapperHandler` e assert su env). Alcuni numeri/esempi sono illustrativi.
  - Azioni: mantenere i diagrammi generali; rimuovere/aggiornare la sezione Signers; allineare provider e flusso al workflow `Query Check → Info Recovery → Report Generation`.

- `Async_Implementation_Detail.md`
  - Stato: aspirazionale/roadmap tecnica.
  - Criticità: la Pipeline è già asincrona per il workflow (`interact_async`), ma i singoli wrappers sono sincroni; il documento descrive dettagli di async su MarketAgent che non esiste come classe separata, e prevede parallelizzazione sui provider non implementata nei wrappers.
  - Azioni: mantenere come proposta di miglioramento; etichettare come "future work"; evitare di confondere con stato attuale.

- `Market_Data_Implementation_Plan.md`
  - Stato: piano di lavoro (utile).
  - Criticità: parla di Binance mock/signers; nel codice attuale esiste `BinanceWrapper` reale (autenticato) e non ci sono signers; la sezione aggregazione JSON è coerente come obiettivo ma non implementata nativamente dai tools (aggregazione base è gestita da `WrapperHandler.try_call_all`).
  - Azioni: aggiornare riferimenti a `BinanceWrapper` reale; chiarire che l’aggregazione avanzata è un obiettivo; mantenere come guida.

- `Piano di Sviluppo.md`
  - Stato: generico e parzialmente disallineato.
  - Criticità: fa riferimento a stack (LangChain/LlamaIndex) non presente; ruoli degli agenti con naming differente; database/persistenza non esiste nel codice.
  - Azioni: etichettare come documento legacy; mantenerlo solo se serve come ispirazione; altrimenti spostarlo in `docs/legacy/`.

- `Progetto Esame.md`
  - Stato: descrizione obiettivo.
  - Criticità: allineata come visione; non problematica.
  - Azioni: mantenere.

## Raccomandazioni

- Aggiornare `App_Architecture_Diagrams.md` rimuovendo la sezione "Signers Architecture" e allineando i diagrammi al workflow reale (`agents/pipeline.py`).
- Aggiungere `Current_Architecture.md` (presente) come riferimento principale per lo stato attuale.
- Spostare `Piano di Sviluppo.md` in `docs/legacy/` o eliminarlo se non utile.
- Annotare `Async_Implementation_Detail.md` e `Market_Data_Implementation_Plan.md` come "proposals"/"future work".

## Elenco Documenti Obsoleti o Parzialmente Obsoleti

- Parzialmente Obsoleti:
  - `App_Architecture_Diagrams.md` (sezione Signers, parti di provider detection)
  - `Async_Implementation_Detail.md` (dettagli Async MarketAgent non implementati)
  - `Market_Data_Implementation_Plan.md` (Binance mock/signers)

- Legacy/Non allineato:
  - `Piano di Sviluppo.md` (stack e ruoli non corrispondenti al codice)

## Nota

Queste raccomandazioni non rimuovono immediatamente file: il mantenimento storico può essere utile. Se desideri, posso eseguire ora lo spostamento in `docs/legacy/` o la cancellazione mirata dei documenti non necessari.