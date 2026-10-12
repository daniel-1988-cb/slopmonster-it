---
name: slopmonster-it
description: Rivede un testo in italiano per chi lo leggerà, controlla le formule tipiche della scrittura da IA, lo riscrive, chiede una seconda revisione a un modello di un'altra famiglia e ricontrolla. Si attiva con /slopmonster-it, "sembra scritto dall'IA", "togli lo slop", "rendilo più umano", "sistema questo testo", "suona artificiale".
---

# SlopMonster IT

Rivedi la bozza per il suo pubblico e il suo scopo. Funziona per README, pagine web,
mail, post e copioni in italiano. Usa il controllo per trovare le formule note, poi
rileggi il testo nel suo contesto. Un 5/5 vuol dire che nessuna regola ha trovato
niente; non dice che il testo è chiaro o corretto.

## Passo 1: capire il contesto e lanciare il controllo

Individua chi legge, il formato e cosa serve a chi legge. Usa le indicazioni
dell'utente e la bozza stessa. Fai una domanda mirata solo se il contesto mancante
cambierebbe davvero la revisione.

Un README spiega cosa fa il progetto, come si usa e i suoi limiti. Una pagina di
vendita può aprire con un problema. Una mail può partire dalla richiesta. Scegli
l'approccio adatto al documento.

```bash
python3 tools/deslop.py bozza.md
python3 tools/deslop.py pagina.html
python3 tools/deslop.py pagina.html --view view-site
python3 tools/deslop.py --text "incolla qui la bozza"
```

Il controllo ha cinque categorie: lessico, costrutti, punteggiatura, elenchi a tre e
possibili prove inventate. Ogni categoria con un riscontro toglie un punto. Sotto il
5/5 esce con codice 1, e anche un testo vuoto esce con 1.

Per il Markdown passa il percorso del file, così codice ed esempi citati vengono
saltati. Le regole sono solo per l'italiano e non riconoscono la lingua.

## Passo 2: rivedere e riscrivere

Leggi [references/segnali-ia.md](references/segnali-ia.md): c'è il catalogo completo,
comprese le voci che lo script non controlla e che vanno guardate a mano.

Lavora sulla bozza in quest'ordine:

1. **Scopo e struttura.** Rispondi presto alla prima domanda del lettore. Togli i
   doppi ganci e le curiosità che rimandano una spiegazione. Ogni paragrafo ha un
   punto utile e il contesto per capirlo.
2. **Significato e prove.** Ogni frase aggiunge qualcosa e segue da quella prima.
   Spiega le condizioni delle affermazioni. Togli contrasti vuoti, metafore ripetute
   e paragoni che non aiutano. Conserva fatti, funzionamento tecnico e posizione
   dell'autore.
3. **Parole e ritmo.** Guarda i riscontri del controllo e sostituisci le parole vaghe
   con parole dirette. Leggi insieme le frasi vicine per trovare forme ripetute. La
   lunghezza delle frasi segue il pensiero. Tieni gli elenchi e la punteggiatura che
   servono.

Mantieni il registro: se la bozza dà del tu resta il tu, se dà del lei resta il lei.
Non fabbricare personalità aggiungendo opinioni, errori, frasi spezzate o una quota
fissa di frasi brevi. Non aggiungere un numero a ogni affermazione. Usa solo fatti
forniti dall'autore o verificati da una fonte adatta.

Il controllo può segnalare italiano corretto. Guarda il riscontro prima di toccarlo.
Non mettere mai testo normale in formato codice per alzare il voto. Se una frase
necessaria fa ancora scattare una regola, spiega il riscontro all'utente.

## Passo 3: chiedere una seconda revisione

Usa una famiglia di modelli diversa da quella che ha scritto la bozza. È una seconda
lettura con lo stesso pubblico e lo stesso scopo: guarda cosa propone prima di
accettarlo.

| Bozza scritta con | Comando |
|---|---|
| Claude | `DESLOP_WRITER=claude tools/cleanse.sh bozza.md > pulito.md` |
| GPT / Codex / ChatGPT | `DESLOP_WRITER=gpt tools/cleanse.sh bozza.md > pulito.md` |
| Gemini | Uno dei due comandi, a seconda della CLI rivale installata. |

Lo script usa il modello configurato nella CLI scelta e
[prompts/cleanse.txt](prompts/cleanse.txt). La CLI deve essere installata e
autenticata. Se non c'è, usa prompt e bozza nella chat dell'altra famiglia. Se non
puoi raggiungere un secondo modello, dillo e continua con la revisione e i controlli
locali.

Lo standard output contiene il testo riscritto, lo standard error le note. Per
tenerli entrambi:

```bash
DESLOP_WRITER=gpt tools/cleanse.sh bozza.md > pulito.md 2> note.txt
```

Controlla il codice d'uscita. Tempo scaduto: 124. CLI rivale mancante: 127, e sullo
standard output c'è il prompt con la bozza, non un testo riscritto. Gli altri errori
della CLI vanno risolti prima di usare il file.

Il modello separa le note con `<<<SLOPMONSTER-NOTES>>>`. Un avviso sul marcatore
mancante vuol dire che le note potrebbero essere finite nel testo: controlla.

## Passo 4: confrontare e ricontrollare

Confronta il risultato con la bozza. Controlla che fatti e comandi non siano cambiati,
che link e segnaposto ci siano ancora, e rileggi l'apertura nel contesto. Guarda le
note per eliminazioni che potrebbero aver tolto informazioni necessarie.

```bash
python3 tools/deslop.py pulito.md
```

Punta a risolvere i riscontri mantenendo il significato. Segnala le eccezioni
motivate. La rilettura finale serve anche a 5/5.

Se cambi una regex, lancia `python3 tools/test_deslop.py`. Se cambi lo script di
revisione, lancia `bash tools/test_cleanse.sh`.

## Fatti

Non inventare mai prove: numeri di clienti, testimonianze, voti, risultati. Se alla
bozza manca un'informazione, segnalala all'autore con un segnaposto come
`[serve un numero]`. Non pubblicare un segnaposto aperto come se fosse un dato.

La regola delle prove vede solo un numero accanto a un nome. Non sa se è vero. Usa
`--allow-proof` solo dopo aver controllato: l'avviso resta, il punto no.

## Uscita

Restituisci il testo riscritto o salva il file richiesto. Poi al massimo cinque note
brevi sulle modifiche importanti e sul risultato del controllo. Di' se la seconda
revisione è stata fatta. Lascia visibili le affermazioni da verificare e i riscontri
rimasti. Non dire che la revisione dimostra che il testo l'ha scritto una persona.
