#!/usr/bin/env python3
"""Cerca i segnali della scrittura da IA nel testo italiano. Regex, nessuna opinione, esce in rosso.

    python3 deslop.py bozza.md                 # Markdown: salta codice, esempi barrati, immagini
    python3 deslop.py pagina.html              # solo il testo che vede chi visita la pagina
    python3 deslop.py pagina.html --view view-site   # valuta un solo blocco
    python3 deslop.py --text "Non è solo un trattamento, è un vero e proprio viaggio."
    python3 deslop.py bozza.md --allow-proof   # i tuoi numeri sono veri e documentati

Versione italiana di SlopMonster (https://github.com/ItsssssJack/SlopMonster, MIT,
Jack Roberts): stesse cinque categorie, stesso voto su 5, stesso codice d'uscita,
stessa gestione di HTML e Markdown. Cambia il catalogo, scritto per l'italiano.

Voto su 5. Sotto il 5 esce con codice 1, apposta: un testo «quasi pulito» è il modo
in cui una pagina finisce per somigliare a tutte le altre pagine scritte da un modello.
"""
import html as _html   # alias: `visible_text` ha un parametro che si chiama `html`
import re
import sys

# ── il catalogo ──────────────────────────────────────────────────────────────
# Raggruppato per il motivo per cui una cosa è un segnale, perché il rimedio cambia.

# Radici: ogni voce prende anche le desinenze. `olistic` trova olistico, olistica,
# olistici, olistiche, olisticamente. Le radici sono scelte lunghe e riconoscibili,
# così il suffisso libero non pesca parole che non c'entrano.
VOCAB = [
    'olistic', 'sinergi', 'paradigm', 'connubi', 'impareggiabil',
    'ineguagliabil', 'imprescindibil', 'meticolos', 'arazz', 'trasformativ',
    'rivoluziona', 'rivoluzioner', 'immersiv', 'indimenticabil', 'sapient',
    'magistral', 'vibrant', 'sfaccettat', 'poliedric', 'variegat', 'resilien',
    'crucial',
    # seconda fascia: una volta in una pagina lunga passa, in ogni paragrafo no
    'innovativ', 'intuitiv', 'affascinant', 'intrinsec',
]

# Frasi con un senso letterale accanto a quello pubblicitario: cercate parola per
# parola, mai per radice, così l'uso innocente sopravvive. «Un panorama sulle colline»
# resta pulito, «nel panorama attuale» no.
VOCAB_EXACT = [
    'a 360 gradi', 'a tutto tondo', "all'insegna", "all'avanguardia", 'pilastro fondamentale',
    'pilastri fondamentali', 'tre pilastri', 'quattro pilastri', 'cinque pilastri', 'nel panorama', "nell'attuale panorama",
    'in continua evoluzione', 'in costante evoluzione', 'in rapida evoluzione',
    "nel mondo di oggi", "al giorno d'oggi", "nell'era digitale", 'nella società odierna',
    'nel mondo moderno', 'mondo frenetico', 'ritmi frenetici', 'in un mondo in cui',
    'in un mondo dove', 'in un mondo sempre più', 'viaggio alla scoperta', 'viaggio verso',
    'intraprendere un viaggio', 'intraprendi un viaggio', 'esperienza unica', 'senza pari',
    'senza precedenti', 'unico nel suo genere', 'livello successivo', 'prossimo livello',
    'una vera svolta', 'game changer', 'game-changer', 'fa la differenza',
    'fare la differenza', 'fanno la differenza', 'farà la differenza', 'il tuo alleato', 'alleato ideale',
    'alleato perfetto', 'prezioso alleato', 'a portata di click', 'a portata di clic',
    'nei minimi dettagli', 'cura dei dettagli', 'attenzione ai dettagli',
    'attenzione al dettaglio', 'lasciati coccolare', 'puro relax', 'regalati un momento',
    'concediti un momento', 'prenditi un momento', 'tutto ciò di cui hai bisogno',
    'tutto quello di cui hai bisogno', "in un batter d'occhio", 'in men che non si dica',
    'sinonimo di', 'pietra miliare', 'perfetto equilibrio', 'equilibrio perfetto',
    'mix perfetto', 'il tuo potenziale', 'pieno potenziale', 'massimo potenziale',
    'scopri il potere', 'sfrutta il potere', 'sfruttare il potere', 'svelare i segreti',
]


def _root_pattern(stem):
    """Un'espressione regolare che trova `stem` e le sue desinenze (fino a 7 lettere)."""
    return rf"(?<!\w){re.escape(stem)}[a-zàèéìòù]{{0,7}}(?!\w)"


# «non solo / soltanto / semplicemente», anche con un verbo in mezzo:
# «non è solo», «non ti aiuta soltanto», «non si tratta solo».
_NEG_SOLO = r"\bnon\s+(?:\w+\s+){0,2}?(?:solo|soltanto|solamente|semplicemente)\b"

PHRASES = [
    # costrutti, non parole: sono i segnali più forti
    (_NEG_SOLO + r"[^.!?]{0,80}\bma\b",            "il costrutto «non solo X, ma Y»"),
    # La seconda metà può arrivare dopo virgola, punto o due punti: «Non è solo una crema.
    # È un rituale.», «non è solo un piacere: è un gesto d'amore». Senza soggetto espresso, il segnale è il verbo che riparte.
    (_NEG_SOLO + r"[^!?]{0,80}?[,.;:]\s*(?:è|sono|bensì)\b", "il costrutto «non è solo X, è Y»"),
    (r"\bnon\s+si\s+tratta\s+(?:solo\s+|soltanto\s+|semplicemente\s+)?di\b[^!?]{0,80}?[,.;:]\s*(?:ma|bensì|si\s+tratta)\b",
                                                   "il costrutto «non si tratta di X, ma di Y»"),
    (r"\bpiù\s+(?:di|che)\s+(?:un[oa]?\s+|un')?semplic|\bben\s+più\s+di\s+(?:un[oa]?\b|un')",
                                                   "«più di un semplice»"),
    (r"\b(?:sia\s+)?che\s+(?:tu|lei|voi)\s+(?:sia|siate|stia|stiate|abbia|abbiate|voglia|vogliate|cerchi|cerchiate|preferisca|preferiate)\b[^.!?]{0,60}\b(?:o|oppure|sia)\b",
                                                   "l'apertura «che tu sia X o Y»"),
    (r"\b(?:ecco\s+(?:dove|perché|che)|è\s+(?:proprio\s+)?qui\s+che|qui)\b[^.!?]{0,25}\bentra(?:no)?\s+in\s+gioco\b",
                                                   "«ecco dove entra in gioco X»"),
    (r"(?<!\w)(?:d[iì]'|dì|dici|dite|diciamo|dire)\s+addio\s+(?:a|al|alla|alle|ai|agli|allo|all')",
                                                   "«di' addio a»"),
    (r"\bimmagin(?:a|ate|ati)\s+(?:un|una|uno|un'|di|il|la|lo|i|le|gli|l'|se|come|quanto|cosa)(?!\w)|\bprov(?:a|ate)\s+ad?\s+immaginare\b",
                                                   "l'apertura «immagina…»"),
    (r"\bin\s+conclusione\b|\bper\s+concludere\b|\bin\s+sintesi\b|\btirando\s+le\s+somme\b|\briassumendo\b",
                                                   "chiusura da tema scolastico"),
    (r"\bquando\s+si\s+tratta\s+di\b",             "riempitivo «quando si tratta di»"),
    (r"\balla\s+fine\s+della\s+giornata,",          "calco «alla fine della giornata»"),
    (r"\bla\s+verità\s+è\s+che\b|\bla\s+chiave\s+(?:è|sta)\b|\bil\s+segreto\s+(?:è|sta)\b"
     r"|\becco\s+la\s+verità\b|\becco\s+il\s+punto\b|\bil\s+bello\s+è\s+che\b|\bla\s+parte\s+migliore\b"
     r"|\bil\s+punto\s+è\s+(?:questo|che)\b|\bsai\s+una\s+cosa\b|\bparliamoci\s+chiaro\b",
                                                   "schiarirsi la voce prima di parlare"),
    (r"\bè\s+(?:importante|fondamentale|essenziale|cruciale|bene|utile|interessante)\s+"
     r"(?:notare|sottolineare|ricordare|evidenziare|precisare|considerare|tenere\s+(?:a\s+mente|presente))\b"
     r"|\bvale\s+la\s+pena\s+(?:di\s+)?(?:notare|sottolineare|ricordare|evidenziare|menzionare|precisare)\b"
     r"|\b(?:va|occorre|bisogna)\s+(?:sottolineato|sottolineare|evidenziato|evidenziare)\b"
     r"|\bè\s+doveroso\s+(?:sottolineare|ricordare|precisare)\b",
                                                   "commento editoriale («è importante sottolineare»)"),
    (r"\b(?:gioca|giocano|riveste|rivestono|svolge|svolgono|ricopre|ricoprono|ha|hanno)\s+un\s+ruolo\s+"
     r"(?:fondamentale|cruciale|chiave|centrale|essenziale|determinante|decisivo|di\s+primo\s+piano)\b"
     r"|\bdi\s+(?:fondamentale|vitale|cruciale|primaria|capitale|estrema)\s+importanza\b",
                                                   "enfasi sull'importanza"),
    (r"\bpotrebbe(?:ro)?\s+(?:potenzialmente|eventualmente|forse|probabilmente)\b"
     r"|\b(?:forse|potenzialmente)\s+potrebbe(?:ro)?\b",
                                                   "cautele accatastate"),
    (r"\b(?:molto|davvero|veramente|estremamente)\s+unic[oaie]\b", "rafforzativo vuoto («davvero unico»)"),
    (r"\b(?:può|possono|potrebbe|potrebbero)\s+aiutarti\s+a\b", "beneficio con le mani avanti («può aiutarti a»)"),
    (r"(?:\b(?:il|la|lo)\s+|\bl')(?:risultato|risposta|segreto|motivo|bello|verità|soluzione|trucco|problema|differenza|novità)\?\s",
                                                   "domanda che si risponde da sola"),
    (r"\b(?:immergiamoci|addentriamoci|tuffiamoci|scopriamolo\s+insieme|senza\s+ulteriori\s+indugi"
     r"|entriamo\s+nel\s+vivo|(?:vediamo|scopriamo|esploriamo|analizziamo|approfondiamo)(?:lo|la|li|le)?\s+insieme)\b",
                                                   "apertura «scopriamolo insieme»"),
    (r"\b(?:sei\s+)?pront[oaie]\s+(?:a|ad|per)\b[^.!?]{0,40}\?|\b(?:cosa|che)\s+aspetti\b"
     r"|\bnon\s+aspettare\s+oltre\b|\bnon\s+lasciarti\s+sfuggire\b|\bnon\s+perdere\s+(?:l'|questa\s+)occasione\b",
                                                   "invito all'azione da modulo"),
    (r"\bnon\s+(?:è|sarà|era)\s+un\s+caso\s+(?:che|se)\b", "«non è un caso che»"),
    (r"\bma\s+non\s+è\s+tutto\b|\bnon\s+finisce\s+qui\b", "«ma non è tutto» da televendita"),
    (r"\b(?:niente|nessun[oa]?|zero|no)\s+[^.!?,:]{1,30},\s+(?:niente|nessun[oa]?|zero|no)\s+[^.!?,:]{1,30}[,.:]\s+(?:solo|soltanto|solamente|semplicemente)\b",
                                                   "il costrutto «niente X, niente Y, solo Z»"),
    (r"\bin\s+quest[oa]\s+(?:articolo|guida|post)\b[^.!?]{0,40}\b(?:esplor|scopr|vedr|analizz|approfond)\w*",
                                                   "annuncio del sommario da blog"),
]

# Connettivi da compito in classe a inizio frase. Uno ci sta, il modello li mette in
# fila: «Inoltre, … Pertanto, … Di conseguenza, …». Conta solo l'inizio della frase,
# perché a metà frase sono italiano normale. Nei testi lunghi la soglia cresce: due
# «Inoltre» in diecimila parole sono un saggio, non un modello.
CONNETTIVI = re.compile(
    r"(?:^|[.!?]\s+)(?:inoltre|pertanto|di\s+conseguenza|in\s+aggiunta|allo\s+stesso\s+modo"
    r"|d'altra\s+parte|altresì|ciononostante|nondimeno)\b")
CONNETTIVI_SOGLIA = 2

# Aggettivi da brochure. Un elenco di tre con almeno due di questi («semplice, veloce
# ed efficace») è il riflesso del tre, non un elenco di cose vere.
AGGETTIVI_BROCHURE = (
    'semplic', 'veloc', 'rapid', 'efficac', 'efficient', 'sicur', 'intuitiv', 'innovativ',
    'personalizzat', 'professional', 'affidabil', 'complet', 'accessibil', 'modern',
    'elegant', 'pratic', 'comod', 'flessibil', 'potent', 'unic', 'autentic', 'esclusiv',
    'sostenibil', 'natural', 'delicat', 'profond', 'duratur', 'visibil', 'funzional',
    'raffinat', 'lussuos', 'rilassant', 'rigenerant', 'avvolgent', 'dinamic', 'facil',
    'trasparent', 'convenient', 'genuin', 'puntual', 'curat', 'smart',
)

# Composti col trattino. In italiano sono rari e quasi sempre prestiti («anti-age»,
# «all-inclusive»): quattro nella stessa frase sono il modello che si dà un tono.
# Solo minuscole: «Bari-Campobasso» o «Jean-Paul» sono nomi propri, non un tono.
COMPOUND = re.compile(r'(?<!\w)[a-zàèéìòù]{2,}-[a-zàèéìòù]{2,}(?:-[a-zàèéìòù]{2,})*(?!\w)')
COMPOUND_FLOOR = 4

# Prove inventate. Larga apposta: è l'unico errore senza ritorno, quindi conta più
# non perderne una che sbagliare qualche volta. Se il numero è vero e documentato,
# --allow-proof lo lascia come avviso. Punto delle migliaia e virgola dei decimali
# all'italiana; il punto conta solo se segue una cifra, così «nel 2000. I clienti…»
# non diventa una cifra di clienti.
PROOF = re.compile(
    r"\d+(?:[.,]\d+)*\s*(?:%|\+)?\s*"
    r"(?:(?:dei|delle|degli|di|tra|fra)\s+(?:nostr[ie]\s+)?)?"
    r"(?:\w+\s+)?"
    r"(?:clienti|utenti|iscritt[ie]|abbonat[ie]|student[ie]|studentesse|aziende|imprese"
    r"|famiglie|pazienti|lettori|lettrici|membri|follower|recensioni|partecipanti"
    r"|professionisti)(?!\w)"
    # voti a stelle: «4,9/5», «4.8 su 5», «4,9 stelle»
    r"|[1-5][.,]\d\s*(?:/\s*5|su\s+5|stelle)(?!\w)",
    re.I)


def normalise(t):
    """Riporta le varianti tipografiche ai caratteri semplici che le regole conoscono.

    Un trattino non separabile non è `-`, \\xa0 non è uno spazio, l'apostrofo curvo
    non è `'`. Senza questo passaggio «nell’era digitale» copiato da Word non viene
    trovato, e Word è proprio da dove arrivano i caratteri tipografici.
    Le lineette restano: le guarda la regola della punteggiatura.
    """
    t = (t.replace('‑', '-').replace('\xa0', ' ').replace('’', "'").replace('‘', "'")
          .replace('“', '"').replace('”', '"').replace('«', '"').replace('»', '"'))
    return re.sub(r'\s+', ' ', t).strip()


def visible_text(html):
    """Quello che legge davvero chi visita: niente script e style, niente tag."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    # Tutte le entità, non un elenco scritto a mano: `&#x27;` lasciato com'è regalava
    # un punto e virgola alla regola della punteggiatura e accecava le altre.
    t = _html.unescape(t)
    return normalise(t)


def read_utf8(path):
    """Legge il file come UTF-8, qualunque sia la codifica del sistema.

    Su Windows open() senza encoding= usa cp1252: lineette e lettere accentate
    diventano spazzatura e le regole tacciono. Un controllo che passa perché non
    sa leggere è peggio di nessun controllo.
    """
    return open(path, encoding='utf-8', errors='replace').read()


def markdown_prose(md):
    """Il testo di un file Markdown, senza gli esemplari.

    Una citazione non è testo pubblicato. Un README che spiega la parola `olistico`
    non l'ha usata, l'ha nominata. Prima del voto escono: blocchi di codice, codice
    in linea, testo barrato (l'esempio sbagliato mostrato apposta) e testo
    alternativo delle immagini. Il testo dei link resta, perché si legge.
    Titoli, celle di tabella, punti elenco e citazioni diventano frasi a sé.
    """
    md = re.sub(r'```.*?```', ' ', md, flags=re.S)
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' . ', md)
    md = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', md)
    # Segnaposto, non cancellazione: togliere `[serve un numero]` incollerebbe la
    # frase in un falso elenco di tre. «ciò» non fa scattare nessuna regola.
    md = re.sub(r'`[^`]*`', ' ciò ', md)
    md = re.sub(r'~~.*?~~', ' ciò ', md, flags=re.S)
    md = re.sub(r'^\s{0,3}#{1,6}\s*(.*)$', r' . \1 . ', md, flags=re.M)
    md = re.sub(r'\|', ' . ', md)
    md = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', ' . ', md, flags=re.M)
    md = re.sub(r'^\s*>\s?', ' . ', md, flags=re.M)
    md = re.sub(r'[*_>]', ' ', md)
    return normalise(md)


def _windows(text):
    """Frasi spezzate in finestre da 220 caratteri.

    Le scritte d'interfaccia (menu, pulsanti, etichette) non hanno punto finale:
    senza la finestra l'intera pagina diventerebbe una sola frase e ogni regola
    di densità scatterebbe sempre. Un controllo che grida al lupo viene spento.
    """
    for s in re.split(r'(?<=[.!?])\s+', text):
        yield [s[i:i + 220] for i in range(0, max(1, len(s)), 220)]


def audit(text):
    hits = {'vocab': [], 'phrases': [], 'punctuation': [], 'rhythm': [], 'proof': []}
    low = text.lower()

    for w in VOCAB:
        n = len(re.findall(_root_pattern(w), low))
        if n:
            hits['vocab'].append((w, n))

    for w in VOCAB_EXACT:
        n = len(re.findall(rf"(?<!\w){re.escape(w)}(?!\w)", low))
        if n:
            hits['vocab'].append((w, n))

    for pat, label in PHRASES:
        found = re.findall(pat, low)
        if found:
            hits['phrases'].append((label, len(found)))

    n = len(CONNETTIVI.findall(low))
    if n >= max(CONNETTIVI_SOGLIA, len(text.split()) // 500):
        hits['phrases'].append(('connettivi da tema in fila a inizio frase', n))

    # Lineetta lunga. Chi scrive in italiano a tastiera non ha il tasto «—» e usa
    # «-» o il «–» che Word mette da solo: la lineetta lunga ripetuta nella stessa
    # frase è la cadenza del modello. Il «–» con gli spazi è tipografia italiana
    # normale per gli incisi e non si conta.
    for windows in _windows(text):
        for w in windows:
            if w.count('—') >= 2:
                hits['punctuation'].append(('due o più lineette lunghe (—) nella stessa frase',
                                            w[:70].strip()))
                break
    for windows in _windows(text):
        for w in windows:
            found = COMPOUND.findall(w)
            if len(found) >= COMPOUND_FLOOR:
                hits['punctuation'].append((f'{len(found)} composti col trattino nella stessa frase',
                                            ', '.join(found[:4])))
                break

    # Soglia 3: due punti e virgola in una pagina tecnica lunga sono uno stile.
    if text.count(';') > max(3, len(text) // 1200):
        hits['punctuation'].append(('troppi punti e virgola per un testo web',
                                    f"{text.count(';')} trovati"))

    # Il riflesso del tre. Due forme, strette apposta.
    #
    # (a) La virgola prima di «e» in un elenco di tre parole: «veloce, semplice, ed
    #     efficace». In italiano non si usa, è un calco della virgola di Oxford.
    # (b) Un elenco di tre con almeno due aggettivi da brochure: «delicato, profondo
    #     e duraturo». «Pulizia, idratazione e massaggio» è un elenco di cose vere e
    #     resta pulito. Si giudica la forma, non il significato.
    for m in re.finditer(r'(?<!\w)(\w{4,}),\s+(\w{4,}),\s+(?:e|ed)\s+(\w{4,})(?!\w)', text):
        hits['rhythm'].append(('virgola prima di «e» in un elenco di tre', m.group(0)[:60]))
    for m in re.finditer(r'(?<!\w)(\w+),\s+(\w+),?\s+(?:e|ed)\s+(\w+)(?!\w)', low):
        brochure = sum(any(p.startswith(a) for a in AGGETTIVI_BROCHURE) for p in m.groups())
        if brochure >= 2:
            hits['rhythm'].append(('elenco di tre aggettivi da brochure', m.group(0)[:60]))

    for m in PROOF.finditer(text):
        hits['proof'].append(m.group(0).strip())

    return hits


def report(hits, label='', allow_proof=False):
    weights = {'vocab': 1, 'phrases': 1, 'punctuation': 1, 'rhythm': 1, 'proof': 1}
    if allow_proof:
        # L'unica regola che una regex non sa giudicare: vede un numero accanto a un
        # nome, non sa se è documentato. --allow-proof mostra ancora gli avvisi ma non
        # fa bocciare per sempre un dato vero.
        weights['proof'] = 0
    failed = [k for k, v in hits.items() if v]
    score = max(0, 5 - sum(weights[k] for k in failed))

    titles = {
        'vocab': 'lessico da IA',
        'phrases': 'costrutti da IA',
        'punctuation': 'punteggiatura',
        'rhythm': 'elenchi a tre',
        'proof': 'possibili prove inventate',
    }

    if label:
        print(f'── {label}')
    for k in ('proof', 'phrases', 'vocab', 'punctuation', 'rhythm'):
        if not hits[k]:
            continue
        print(f'  {titles[k]}:')
        for item in hits[k][:8]:
            print(f'    · {item[0] if isinstance(item, tuple) else item}'
                  + (f'  ({item[1]})' if isinstance(item, tuple) and len(item) > 1 else ''))
        if len(hits[k]) > 8:
            print(f'    · …e altri {len(hits[k]) - 8}')

    print(f'\n  voto {score}/5', end='  ')
    print('PULITO' if score == 5 else 'da ripulire')
    return score


if __name__ == '__main__':
    # Una console Windows è cp1252: un'emoji in un estratto segnalato chiuderebbe il
    # giro con un UnicodeEncodeError. Meglio sostituire il carattere che crollare.
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass

    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    allow_proof = '--allow-proof' in args
    args = [a for a in args if a != '--allow-proof']

    as_md = '--markdown' in args
    args = [a for a in args if a != '--markdown']

    if args[0] == '--text':
        text = ' '.join(args[1:])
        text = markdown_prose(text) if as_md else normalise(text)
    elif args[0].endswith('.md') or as_md:
        try:
            text = markdown_prose(read_utf8(args[0]))
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            sys.exit(f'deslop: impossibile leggere {args[0]}: {e.strerror}')
    else:
        try:
            html = read_utf8(args[0])
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            sys.exit(f'deslop: impossibile leggere {args[0]}: {e.strerror}')
        if '--view' in args:
            # valuta un solo blocco: dal suo id= al prossimo id="view-…"
            vid = args[args.index('--view') + 1]
            start = html.find(f'id="{vid}"')
            if start < 0:
                sys.exit(f'nessun elemento con id "{vid}"')
            nxt = html.find('id="view-', start + 1)
            html = html[start:nxt if nxt > 0 else len(html)]
        text = visible_text(html)

    # Niente da valutare è una bocciatura, non una promozione: una pulizia scaduta
    # lascia un file vuoto, e un controllo che lo timbra PULITO mente proprio quando
    # la catena si è rotta.
    if not text.split():
        sys.exit('deslop: nessun testo da valutare, input vuoto')

    print(f'{len(text.split())} parole di testo visibile\n')
    sys.exit(0 if report(audit(text), allow_proof=allow_proof) == 5 else 1)
