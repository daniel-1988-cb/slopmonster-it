# SlopMonster IT

Versione italiana di [SlopMonster](https://github.com/ItsssssJack/SlopMonster) di Jack
Roberts. Controlla un testo in italiano, segnala le formule tipiche della scrittura
generata da un modello linguistico e dà le istruzioni per riscriverlo. Serve per una
pagina web, una mail, un post, un README o un copione.

Il controllo è uno script Python che assegna un voto su 5. La riscrittura la fa un
agente (Claude, Codex o un altro) seguendo [SKILL.md](SKILL.md), poi un modello di
un'altra famiglia rilegge il testo e lo script controlla di nuovo.

L'originale riconosce solo l'inglese: su un testo italiano dà 5/5 perché non trova
niente. Questa versione ha un catalogo scritto da capo per l'italiano.

## Partire subito

Serve Python 3, senza pacchetti da installare e senza chiavi.

```bash
git clone https://github.com/daniel-1988-cb/slopmonster-it
cd slopmonster-it

# Una frase al volo.
python3 tools/deslop.py --text "Non è solo un trattamento, è un vero rituale. Il risultato? Pelle nuova."
# Voto 4/5, esce con codice 1.

# Un file Markdown.
python3 tools/deslop.py bozza.md

# Il testo visibile di una pagina HTML.
python3 tools/deslop.py index.html
```

Ogni categoria con almeno un riscontro toglie un punto, quanti che siano i riscontri.
A 5/5 il comando esce con 0, sotto con 1. Anche un testo vuoto esce con 1. Il file
controllato non viene modificato.

Nei file Markdown lo script salta blocchi di codice, codice in linea, immagini e testo
barrato, così puoi citare un esempio sbagliato senza essere bocciato. Nell'HTML toglie
tag, script e stili. Non disegna la pagina, quindi conta anche il testo nascosto via CSS.

## Cosa segnala

| Categoria | Cosa cerca | Esempi |
|---|---|---|
| Lessico | Parole e frasi fatte da brochure, con le loro desinenze | `olistico`, `sinergia`, `all'avanguardia`, `a 360 gradi`, `fa la differenza`, `il tuo alleato` |
| Costrutti | Forme di frase ricorrenti nei testi generati | `non è solo X, è Y`, `che tu sia X o Y`, `il risultato? …`, `scopriamolo insieme`, `è importante sottolineare che` |
| Punteggiatura | Lineetta lunga ripetuta nella stessa frase, quattro composti col trattino, troppi punti e virgola | `il metodo — testato — funziona` |
| Elenchi a tre | La virgola prima della `e` finale, oppure tre aggettivi da brochure in fila | `semplice, veloce ed efficace` |
| Prove | Un numero vicino a clienti, utenti, recensioni, oppure un voto a stelle | `oltre 10.000 clienti`, `4,9/5` |

Il catalogo completo, con le voci da guardare a mano, è in
[references/segnali-ia.md](references/segnali-ia.md).

Qualche scelta pensata per l'italiano:

- **La lineetta lunga sì, quella media no.** A tastiera non c'è il tasto per `—`, e Word
  trasforma da solo il trattino in `–`. Un inciso tra due `–` con gli spazi è tipografia
  italiana normale e resta pulito; due `—` nella stessa frase vengono quasi sempre da un
  modello.
- **La virgola prima della `e`** in un elenco di tre è un calco dall'inglese. In
  italiano non si mette, e i modelli la mettono.
- **I connettivi in fila.** `Inoltre`, `Pertanto`, `Di conseguenza` a inizio frase sono
  italiano corretto. Ne segnala due o più in un testo breve; nei testi lunghi la soglia
  cresce.
- **Numeri all'italiana.** Punto per le migliaia, virgola per i decimali: `10.000 clienti`
  è una cifra, `nel 2000. I clienti` no.

Il voto è stato provato anche su voci di Wikipedia in italiano scritte da persone. Le
regole che scattavano sull'uso normale della lingua sono state ristrette o tolte: per
esempio `vero e proprio`, che compariva in cinque voci su sette, adesso è solo nel
catalogo da guardare a mano.

## Riscrivere una bozza

Dai all'agente [SKILL.md](SKILL.md) e la bozza. Se non si capisce dal testo, digli chi lo
leggerà e dove verrà pubblicato.

1. Lancia il controllo per vedere cosa riconosce.
2. Rivedi scopo e ordine del testo: un README spiega lo strumento e come si usa, una
   mail dice subito perché scrive.
3. Riscrivi i passaggi vaghi o ripetuti. Ogni frase deve aggiungere qualcosa, e ogni
   affermazione deve stare nei fatti forniti.
4. Chiedi una seconda revisione a un modello di un'altra famiglia, guarda cosa ha
   cambiato e lancia di nuovo il controllo.

La seconda revisione usa [prompts/cleanse.txt](prompts/cleanse.txt). Con la CLI
dell'altra famiglia installata e autenticata:

```bash
# Ha scritto Claude: rilegge Codex.
DESLOP_WRITER=claude tools/cleanse.sh bozza.md > pulito.md

# Ha scritto GPT: rilegge Claude.
DESLOP_WRITER=gpt tools/cleanse.sh bozza.md > pulito.md

# Leggi il risultato e controllalo.
python3 tools/deslop.py pulito.md
```

Il testo riscritto esce sullo standard output, le note sulle modifiche sullo standard
error. Se manca la CLI giusta, lo script stampa il prompt con la bozza da incollare
nella chat dell'altra famiglia ed esce con 127. Se scade il tempo esce con 124.
Controlla il codice d'uscita prima di usare il file.

Un esempio completo, da 1/5 a 5/5, è in [examples/pasticceria.md](examples/pasticceria.md).
Mostra anche il limite: la pulizia ha tolto le formule e anche il calore, e il dettaglio
che manca lo deve dare l'autore.

### Come skill di Claude Code

Copia la cartella in `~/.claude/skills/slopmonster-it/` e chiamala con `/slopmonster-it`.
Per Codex o un altro agente, chiedigli di seguire [SKILL.md](SKILL.md).

## Oltre il voto

Un 5/5 vuol dire che lo script non ha trovato niente di quello che conosce. Prima di
accettare una riscrittura, rileggi il testo dove verrà letto:

- **Lettore e scopo.** Risponde alle domande probabili di chi legge, al livello giusto?
- **Apertura.** Il primo paragrafo spiega di cosa si parla, o rimanda?
- **Filo.** Ogni frase parte da quella prima? Via metafore ripetute e contrasti vuoti.
- **Affermazioni.** Puoi dimostrare ogni fatto? Le condizioni stanno accanto alla frase.
- **Voce.** Il registro è quello dell'autore? Tu o lei, frasi lunghe o brevi: non si
  cambiano per sembrare più umani.

Non aggiungere mai un numero o una testimonianza per rendere una frase più concreta. Se
manca un dato, segnalalo all'autore con un segnaposto come `[serve un numero]`.

### Limiti

Il controllo usa regole scritte a mano per l'italiano e non riconosce la lingua: un
testo in inglese passa pulito. Può segnalare frasi normali e lasciar passare testi
scritti male. Non sa chi ha scritto il testo, non verifica i fatti e non giudica se
un'apertura va bene per il pubblico. Prendi i riscontri come domande da farti.

Se un numero segnalato è vero e documentato:

```bash
python3 tools/deslop.py index.html --allow-proof
```

Gli avvisi restano, ma non tolgono il punto.

## Nei controlli automatici

Siccome sotto 5/5 il comando esce con 1, puoi metterlo nei controlli automatici di un
repository (CI). Il [workflow](.github/workflows/slop.yml) di questo repo lancia i test e
controlla questo README e un testo d'esempio. Copialo e cambia i percorsi dei file.

```bash
python3 tools/test_deslop.py
bash tools/test_cleanse.sh
python3 tools/deslop.py README.md
```

## Da dove viene

- Struttura, voto, gestione di HTML e Markdown, script di revisione e test:
  [SlopMonster](https://github.com/ItsssssJack/SlopMonster), licenza MIT.
- Catalogo italiano: scritto da capo per questo repo e controllato su voci di
  Wikipedia scritte da persone.
- Sullo stesso tema, per l'italiano:
  [claude-skill-scrittura-italiana](https://github.com/hypnosdesign/claude-skill-scrittura-italiana),
  una skill di revisione più ampia (licenza CC BY-SA 4.0, niente è copiato da lì).

[Licenza MIT](LICENSE).
