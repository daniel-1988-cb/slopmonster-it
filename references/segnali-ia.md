# Segnali della scrittura da IA in italiano: il catalogo

Questo catalogo elenca le formule da guardare durante una revisione. Le stesse formule
compaiono anche nella scrittura delle persone: un riscontro è una domanda, non una
condanna. Le regole automatiche complete sono in `tools/deslop.py`; qui ci sono anche le
voci che una regex non sa giudicare e che vanno guardate a mano.

Le cinque sezioni seguono le categorie del voto.

---

## 1 · Lessico

Parole da brochure che dicono poco. Lo script le cerca per radice (prende tutte le
desinenze) o parola per parola quando hanno anche un senso letterale.

**Controllate dallo script, per radice:**
`olistico` · `sinergia` · `paradigma` · `connubio` · `impareggiabile` ·
`ineguagliabile` · `imprescindibile` · `meticoloso` · `arazzo` · `trasformativo` ·
`rivoluzionario` / `rivoluzionerà` · `immersivo` · `indimenticabile` · `sapiente` ·
`magistrale` · `vibrante` · `sfaccettato` / `sfaccettature` · `poliedrico` ·
`variegato` · `resilienza` · `cruciale` · `sbloccare` · `innovativo` · `intuitivo` ·
`affascinante` · `intrinseco`

**Controllate dallo script, parola per parola:**
`a 360 gradi` · `a tutto tondo` · `all'insegna` · `all'avanguardia` ·
`nel panorama` · `in continua evoluzione` · `al giorno d'oggi` · `nell'era digitale` ·
`mondo frenetico` · `in un mondo in cui` · `viaggio alla scoperta` · `esperienza unica` ·
`senza precedenti` · `livello successivo` · `una vera svolta` · `fa la differenza` ·
`il tuo alleato` · `alleato ideale` · `nei minimi dettagli` · `lasciati coccolare` ·
`concediti un momento` · `tutto ciò di cui hai bisogno` · `sinonimo di` ·
`pietra miliare` · `perfetto equilibrio` · `il tuo potenziale` · `scopri il potere`

**Da guardare a mano** (troppo comuni nell'italiano scritto da persone per toglierci un
punto, ma i modelli le usano molto di più):
`vero e proprio` · `fondamentale` · `essenziale` · `eccellenza` · `ecosistema` ·
`percorso` · `valorizzare` · `ottimizzare` · `garantire` · `al fine di` ·
`nell'ottica di` · `performante` · `implementare` · `scopri di più` · `ti aiuta a`

Rimedio: di' cosa succede. `Un approccio olistico` diventa cosa fate davvero, in che
ordine, per quanto tempo.

## 2 · Costrutti

Forme di frase, non parole. Sono i segnali più forti.

| Forma | Esempio | Rimedio |
|---|---|---|
| Negazione e rilancio | `non è solo un trattamento, è un rituale` · `non solo pulisce, ma nutre` · `non si tratta di estetica, ma di salute` | Di' la cosa una volta, in positivo |
| Paragone gonfiato | `più di un semplice massaggio` | Descrivi cosa c'è in più |
| Pubblico doppio | `che tu sia un principiante o un esperto` | Scegli a chi parli |
| Entra in gioco | `ecco dove entra in gioco il nostro metodo` | Presenta il metodo e basta |
| Di' addio | `di' addio alla pelle secca` | Di' cosa cambia |
| Immagina | `immagina una pelle che respira` | Descrivi un caso vero |
| Domanda e risposta | `Il risultato? Pelle più morbida.` | Una frase sola |
| Invito a scoprire | `scopriamolo insieme` · `immergiamoci` · `senza ulteriori indugi` | Entra nell'argomento |
| Schiarirsi la voce | `la verità è che` · `il segreto è` · `sai una cosa?` | Togli e parti dal punto |
| Commento editoriale | `è importante sottolineare che` · `vale la pena ricordare` | Dillo e basta |
| Enfasi d'importanza | `gioca un ruolo fondamentale` · `di vitale importanza` | Spiega perché conta |
| Cautele accatastate | `potrebbe potenzialmente` | Un verbo, con la certezza vera |
| Rafforzativo vuoto | `davvero unico` | Di' cosa lo distingue |
| Beneficio con le mani avanti | `può aiutarti a` | Di' cosa fa, con le sue condizioni |
| Invito da modulo | `sei pronta a cambiare?` · `cosa aspetti?` · `non lasciarti sfuggire` | Un invito preciso: chi, cosa, come |
| Non è un caso | `non è un caso che funzioni` | Spiega il motivo |
| Televendita | `ma non è tutto` · `non finisce qui` | Togli |
| Niente, niente, solo | `niente stress, niente attese: solo relax` | Una frase concreta |
| Sommario da blog | `in questo articolo esploreremo` | Parti dalla prima informazione |
| Chiusura da tema | `in conclusione` · `per concludere` · `tirando le somme` | Chiudi con l'ultima cosa utile, o non chiudere |
| Connettivi in fila | `Inoltre, … Pertanto, … Di conseguenza, …` a inizio frase | Lascia che le frasi si leghino da sole |

## 3 · Punteggiatura

- **Lineetta lunga ripetuta.** Due `—` nella stessa frase. A tastiera la lineetta lunga
  non c'è e Word mette `–`: un inciso tra due `–` resta pulito, due `—` vengono quasi
  sempre da un modello. Rimedio: virgole, due punti o un punto.
- **Composti col trattino in fila.** Quattro nella stessa frase (`anti-age, cruelty-free,
  all-inclusive, made-in-italy`). I nomi propri con le maiuscole non contano.
- **Troppi punti e virgola** per un testo web.

**Da guardare a mano:** titoli con tutte le parole in maiuscolo (`Scopri I Nostri
Trattamenti`, un calco dall'inglese), grassetto in ogni frase, emoji come punti elenco,
punti esclamativi in fila.

## 4 · Elenchi a tre

- **Virgola prima della `e` finale** (`veloce, semplice, ed efficace`): in italiano non
  si mette, è la virgola di Oxford dell'inglese.
- **Tre aggettivi da brochure** con almeno due presi dall'elenco in `tools/deslop.py`
  (`semplice, veloce ed efficace` · `delicato, profondo e duraturo`). Un elenco di cose
  vere (`pulizia, idratazione e massaggio`) resta pulito.

Gli elenchi di tre vanno benissimo quando le cose sono tre. Il segnale è il riflesso,
non il numero.

## 5 · Prove

Un numero accanto a clienti, utenti, iscritti, aziende, famiglie, pazienti, lettori,
membri, follower, recensioni, partecipanti o professionisti (`oltre 10.000 clienti`,
`il 98% delle clienti`), oppure un voto a stelle (`4,9/5`, `4,8 stelle`).

La regola è larga apposta: un numero inventato è l'unico errore che non si recupera.
Non sa se il numero è vero. Se lo è e lo puoi documentare, usa `--allow-proof`: l'avviso
resta, il punto no. Se non lo è, togli il numero o chiedilo all'autore con
`[serve un numero]`.
