# Differenze fra prompt
Resoconto fatto da Claude 4.5

## Query Check
- Prolisso (~50 righe), regole ripetitive
- Mancava contesto temporale
+ Conciso (~40 righe), regole chiare
+ Aggiunto {{CURRENT_DATE}} placeholder (sostituito automaticamente)
+ Schema JSON singolo e diretto

## Team Market
- Non enfatizzava priorità dati API
- Mancavano timestamp nei report
+ Sezione "CRITICAL DATA RULE" su priorità real-time
+ Timestamp OBBLIGATORI per ogni prezzo
+ Richiesta fonte API esplicita
+ Warning se dati parziali/incompleti
+ **DIVIETO ESPLICITO** di inventare prezzi placeholder

## Team News
- Output generico senza date
- Non distingueva dati freschi/vecchi
+ Date pubblicazione OBBLIGATORIE
+ Warning se articoli >3 giorni
+ Citazione fonti API
+ Livello confidenza basato su quantità/consistenza

## Team Social
- Sentiment senza contesto temporale
- Non tracciava platform/engagement
+ Timestamp post OBBLIGATORI
+ Warning se post >2 giorni
+ Breakdown per platform (Reddit/X/4chan)
+ Livello engagement e confidenza

## Team Leader
- Non prioritizzava dati freschi da agenti
- Mancava tracciamento recency
+ Sezione "CRITICAL DATA PRINCIPLES" (7 regole, aggiunte 2)
+ "Never Override Fresh Data" - divieto esplicito
+ Sezioni "Data Freshness" e "Sources" obbligatorie
+ Timestamp per OGNI blocco dati
+ Metadata espliciti su recency
+ **NEVER FABRICATE** - divieto di inventare dati
+ **NO EXAMPLES AS DATA** - divieto di usare dati esempio come dati reali

## Report Generation
- Formattazione permissiva
- Non preservava timestamp/sources
+ "Data Fidelity" rule
+ "Preserve Timestamps" obbligatorio
+ Lista ❌ DON'T / ✅ DO chiara (aggiunte 2 regole)
+ Esempio conditional logic
+ **NEVER USE PLACEHOLDERS** - divieto di scrivere "N/A" o "Data not available"
+ **NO EXAMPLE DATA** - divieto di usare prezzi placeholder

## Fix Tecnici Applicati
1. **`__init__.py` modificato**: Il placeholder `{{CURRENT_DATE}}` ora viene sostituito automaticamente con `datetime.now().strftime("%Y-%m-%d")` al caricamento dei prompt
2. **Regole rafforzate**: Aggiunte regole esplicite contro l'uso di dati placeholder o inventati
3. **Conditional rendering più forte**: Specificato che se una sezione manca, va COMPLETAMENTE omessa (no headers, no "N/A")