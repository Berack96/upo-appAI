# Implementazione Bot Telegram (Python + InlineKeyboard)

Il progetto si basa sulla libreria **`python-telegram-bot`** e sull'uso di **`InlineKeyboard`** per gestire le scelte dell'utente, assicurando un'interfaccia rapida e pulita.

## 1. Setup e Flusso Iniziale

### Inizializzazione

Dovrai innanzitutto inizializzare l'oggetto bot con il tuo **token API** di Telegram e configurare l'**Application** (o il Dispatcher).

### Handler Principali

* **Comando `/start`** : Implementa l'handler per questo comando. La sua funzione è inviare un messaggio di benvenuto e presentare immediatamente la prima **`InlineKeyboard`** per la scelta della strategia (A/B).

## 2. Gestione dei Menu (InlineKeyboard)

Per le scelte di Strategia (A/B) e LLM (Dropdown), la soluzione è basata interamente sulla gestione delle **`InlineKeyboard`** e dei `CallbackQuery`.

### Tasti e Azioni

* **Strategia (A/B)** : Crea una `InlineKeyboard` con i pulsanti 'A' e 'B', ciascuno con un `callback_data` univoco (es. `strategy_A`).
* **Selezione LLM** : Dopo la scelta della strategia, invia una nuova `InlineKeyboard` per la selezione dell'LLM (es. GPT-3.5, Gemini), assegnando un `callback_data` (es. `llm_gpt35`) ad ogni opzione.
* **`CallbackQuery` Handler** : Un unico handler catturerà la pressione di tutti questi pulsanti. Questo gestore deve analizzare il `callback_data` per determinare quale scelta è stata fatta.

### Gestione dello Stato

È fondamentale utilizzare un meccanismo (come il **`ConversationHandler`** della libreria o un sistema di stato personalizzato) per **memorizzare le scelte** dell'utente (`Strategia` e `LLM`) man mano che vengono fatte, guidando il flusso verso la fase successiva.

## 3. Interazione con la LLM e Output

### Acquisizione del Prompt

* **Prompt Handler** : Dopo che l'utente ha selezionato sia la Strategia che l'LLM, il bot deve attendere un **messaggio di testo** dall'utente. Questo handler si attiverà solo quando lo stato dell'utente indica che le scelte iniziali sono state fatte.

### Feedback e Output (Gestione degli aggiornamenti)

Questo è il punto cruciale per evitare lo spam in chat:

1. **Indicatore di Lavoro** : Appena ricevuto il prompt, invia l'azione **`ChatAction.TYPING`** (`sta scrivendo...`) per dare feedback immediato all'utente.
2. **Messaggio Placeholder** : Invia un messaggio iniziale (es. "Elaborazione in corso, attendere...") e  **memorizza il suo `message_id`** .
3. **Aggiornamento in Tempo Reale** : Per ogni *output parziale* (`poutput`) ricevuto dalla tua LLM, utilizza la funzione **`edit_message_text`** passando l'ID del messaggio memorizzato. Questo aggiornerà continuamente l'unico messaggio esistente in chat.
4. **Output Finale** : Una volta che la LLM ha terminato, esegui l'ultima modifica del messaggio (o inviane uno nuovo, a tua discrezione) e **resetta lo stato** dell'utente per un nuovo ciclo di interazione.

### Gestione degli Errori

Integra un gestore di eccezioni (`try...except`) per catturare eventuali errori durante la chiamata all'API della LLM, inviando un messaggio informativo e di scuse all'utente.
