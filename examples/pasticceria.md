# Esempio: la pagina di una pasticceria

Un giro vero, registrato il 12 ottobre 2026. La bozza l'ha scritta Claude, la pulizia
l'ha fatta Codex con `tools/cleanse.sh`. La pasticceria non esiste: è un esempio.

## Prima: voto 1/5

> Nel mondo frenetico di oggi, concedersi un momento di dolcezza non è solo un piacere:
> è un vero gesto d'amore verso sé stessi. Che tu sia un amante dei classici o un
> esploratore di sapori nuovi, la nostra pasticceria è il tuo alleato ideale.
>
> Ogni dolce è curato nei minimi dettagli — dalla scelta delle farine alla cottura —
> per offrirti un'esperienza unica. Il segreto? Ingredienti semplici, freschi e genuini.
>
> Scopri il nostro laboratorio in via Roma 12, aperto dal martedì alla domenica dalle 7
> alle 13.

```text
  costrutti da IA:
    · il costrutto «non è solo X, è Y»  (1)
    · l'apertura «che tu sia X o Y»  (1)
    · domanda che si risponde da sola  (1)
  lessico da IA:
    · mondo frenetico  (1)
    · esperienza unica  (1)
    · il tuo alleato  (1)
    · alleato ideale  (1)
    · nei minimi dettagli  (1)
  punteggiatura:
    · due o più lineette lunghe (—) nella stessa frase  (Ogni dolce è curato nei minimi dettagli — dalla scelta delle farine al)
  elenchi a tre:
    · elenco di tre aggettivi da brochure  (semplici, freschi e genuini)

  voto 1/5  da ripulire
```

## Comando

```bash
tools/cleanse.sh bozza.md > pulito.md 2> note.txt
python3 tools/deslop.py pulito.md
```

## Dopo: voto 5/5

> Pasticceria Rossi prepara dolci classici e nuove proposte nel laboratorio di via
> Roma 12.
>
> Ogni dolce nasce da ingredienti semplici e freschi, con attenzione alla scelta delle
> farine e alla cottura.
>
> Il laboratorio è aperto dal martedì alla domenica, dalle 7 alle 13.

Le note di Codex:

```text
- Tolti ganci generici, formule da brochure e contrasti non necessari.
- Mantenuto il tono diretto con il tu implicito, senza aggiungere fatti nuovi.
- Conservati indirizzo, giorni e orari presenti nel testo originale.
```

## Cosa guardare a mano

Il 5/5 dice che il controllo non trova più niente. Non dice che il testo è buono.
Qui la pulizia ha tolto anche il calore: la pagina adesso è corretta ma fredda, e non
dice perché scegliere questa pasticceria invece di un'altra. Il passo giusto è chiedere
all'autore un dettaglio vero (una ricetta di famiglia, un dolce che fanno solo loro) e
non inventarlo.
