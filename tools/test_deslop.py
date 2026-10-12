#!/usr/bin/env python3
"""Test di regressione del controllo. Si lancia con: python3 tools/test_deslop.py

Due direzioni, e la seconda è quella che conta. È facile allargare una regex finché
prende tutto, quindi ogni regola qui ha accanto un caso che DEVE restare pulito e che
si rompe se la regola diventa ingorda.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deslop import VOCAB_EXACT, audit, visible_text, markdown_prose, PROOF

fails = []


def check(name, cond, detail=''):
    if not cond:
        fails.append(f'{name}: {detail}')


def groups(text):
    return {k for k, v in audit(text).items() if v}


# ── ogni voce del catalogo scatta nella sua forma ────────────────────────────
for w in VOCAB_EXACT:
    check(f'forma esatta «{w}»', 'vocab' in groups(f'Ecco {w} per te.'), 'non trovata')

# ── le desinenze scattano anche loro ─────────────────────────────────────────
for w in ('olistico', 'olistiche', 'sinergia', 'sinergiche', 'rivoluzionario',
          'rivoluzionerà', 'immersiva', 'indimenticabili', 'meticolosamente',
          'sfaccettature', 'imprescindibile', "all'avanguardia", 'sbloccare'):
    check(f'desinenza «{w}»', 'vocab' in groups(f'Un metodo {w} per tutti.'), 'mancata')

# ── i sensi letterali NON devono scattare ────────────────────────────────────
for ok in ('Dalla terrazza si vede un panorama sulle colline.',
           'La rivoluzione francese inizia nel 1789.',
           'Il viaggio in treno dura tre ore.',
           'Ha lavorato venti ore di straordinari.',
           'Il nostro alleato storico è la Francia.',
           'Il portico poggia su quattro pilastro e due archi.',
           'Il futurismo fu un movimento di avanguardia.',
           'La squadra gioca in Eccellenza.'):
    check('senso letterale pulito', 'vocab' not in groups(ok), f'{ok} -> {audit(ok)["vocab"]}')

# ── costrutti ────────────────────────────────────────────────────────────────
for bad in ('Non è solo un trattamento, è un rituale.',
            'Non è solo una crema. È un gesto per te.',
            'Non è solo un piacere: è un gesto d’amore.',
            'Non ti aiuta soltanto a dormire, ma ti rimette in forma.',
            'Non solo pulisce la pelle, ma la nutre.',
            "Non si tratta di estetica, ma di salute.",
            'È più di un semplice massaggio.',
            'Che tu sia un principiante o un esperto, inizia da qui.',
            'Ecco dove entra in gioco il nostro metodo.',
            "Di' addio alla pelle secca.",
            'Immagina una pelle che respira.',
            'In conclusione, il metodo funziona.',
            'Quando si tratta di pelle, serve cura.',
            'La verità è che nessuno te lo dice.',
            'È importante sottolineare che i risultati variano.',
            'La dieta gioca un ruolo fondamentale.',
            'Questo potrebbe potenzialmente aiutare.',
            'Il risultato? Pelle più morbida.',
            'Scopriamolo insieme.',
            'Immergiamoci nel mondo della cosmesi.',
            'Sei pronta a cambiare?',
            'Cosa aspetti?',
            'Non è un caso che funzioni.',
            'Ma non è tutto: c’è anche lo sconto.',
            'Niente stress, niente attese: solo relax.',
            'In questo articolo esploreremo i benefici del sonno.',
            'Un prodotto davvero unico.',
            'Inoltre, è comodo. Pertanto, conviene. Di conseguenza, lo scegli.'):
    check('costrutto trovato', 'phrases' in groups(bad), bad)

for clean in ('Controlla che tu sia sull’ultima versione.',
              'Non è solo una questione di soldi.',
              'Non devi solo fidarti della mia parola.',
              'Il parcheggio non è asfaltato, è sterrato.',
              'Ha detto che il prezzo non era giusto, e siamo usciti.',
              'Inoltre, il centro è aperto anche il sabato.',
              'Il gioco entra nel vivo al secondo tempo.',
              'Il tempo è pronto a cambiare.',
              'Quanto costa? Sessanta euro.'):
    check('costrutto resta pulito', 'phrases' not in groups(clean), f'{clean} -> {audit(clean)["phrases"]}')

# ── elenchi a tre ────────────────────────────────────────────────────────────
check('virgola di Oxford', 'rhythm' in groups('È veloce, semplice, ed efficace.'))
check('aggettivi da brochure', 'rhythm' in groups('Un trattamento delicato, profondo e duraturo.'))
check('aggettivi da brochure senza virgola finale', 'rhythm' in groups('Semplice, veloce ed efficace.'))
for ok in ('Pulizia, idratazione e massaggio viso.',
           'Abbiamo comprato pane, latte e uova.',
           'Lunedì, mercoledì e venerdì siamo aperti fino alle venti.',
           'Si fa in tre passaggi: detersione, maschera e crema.',
           'Il servizio è veloce, gentile e ben fatto.'):
    check('elenco di cose vere resta pulito', 'rhythm' not in groups(ok), f'{ok} -> {audit(ok)["rhythm"]}')

# ── prove ────────────────────────────────────────────────────────────────────
for hit in ('Oltre 10.000 clienti soddisfatte.', 'Scelto da 500 aziende.',
            'Il 98% delle clienti torna.', 'Valutazione 4,9/5.', '4.8 stelle su Google.',
            'Più di 3.000 nuove iscritte.', 'Abbiamo 1.200 recensioni.'):
    check('prova trovata', PROOF.search(hit), hit)
for clean in ('Aperti dal 2001. I clienti tornano.',
              'Nel 2000. Le aziende chiudevano.',
              'Versione 2.0. I lettori possono saltarla.',
              'Il trattamento dura 45 minuti.',
              'Abbiamo 12 cabine.'):
    check('la prova non attraversa il punto', not PROOF.search(clean), clean)
check('il nome deve finire lì', not PROOF.search('Abbiamo 40 clientini affezionati.'))

# ── punteggiatura ────────────────────────────────────────────────────────────
check('due lineette lunghe', 'punctuation' in groups('Il metodo — testato — funziona.'))
check('inciso con «–» resta pulito',
      'punctuation' not in groups('Il centro – aperto dal 1998 – offre trattamenti viso.'))
check('una sola lineetta lunga resta pulita', 'punctuation' not in groups('Il metodo — testato da noi.'))
stack = 'Un prodotto anti-age, all-inclusive, cruelty-free, made-in-italy.'
check('quattro composti col trattino', 'punctuation' in groups(stack), stack)
check('un composto solo resta pulito', 'punctuation' not in groups('Una crema anti-age leggera.'))
check('nomi propri col trattino restano puliti',
      'punctuation' not in groups('Le linee Bari-Campobasso, Roma-Napoli, Jean-Paul e Pierre-Martial.'))

# ── entità: decodificate, non trapelate ─────────────────────────────────────
t = visible_text('<p>Nell&#x27;era digitale non &egrave; solo un sito, &egrave; un ecosistema.</p>')
check('apostrofo da entità decodificato', "nell'era digitale" in t.lower(), repr(t))
check('le entità non regalano punti e virgola', t.count(';') == 0, repr(t))
check('costrutto visto attraverso le entità', 'phrases' in groups(t), repr(t))
check('nbsp diventa spazio', visible_text('<p>a&nbsp;b</p>') == 'a b')
check('apostrofo curvo normalizzato', 'vocab' in groups(visible_text('<p>Nell’era digitale.</p>')))

# ── il cancello: input vuoto boccia, non promuove ───────────────────────────
here = os.path.dirname(os.path.abspath(__file__))
r = subprocess.run([sys.executable, f'{here}/deslop.py', '--text', ''], capture_output=True, text=True)
check('input vuoto esce con errore', r.returncode != 0, f'exit {r.returncode}')
r = subprocess.run([sys.executable, f'{here}/deslop.py', '/non/esiste.html'], capture_output=True, text=True)
check('file mancante esce con errore', r.returncode != 0, f'exit {r.returncode}')
check('file mancante senza traceback', 'Traceback' not in r.stderr, r.stderr[:80])

# ── i file si leggono in UTF-8, qualunque sia il sistema ─────────────────────
_dir = tempfile.mkdtemp()
_tells = ('Non è solo uno strumento, è un ecosistema. Che tu sia un’azienda o un privato, '
          'lavoriamo veloci — davvero veloci — ogni settimana.')
for name, body in (('utf8.html', f'<html><body><p>{_tells}</p></body></html>'),
                   ('utf8.md', _tells)):
    path = os.path.join(_dir, name)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(body)
    r = subprocess.run([sys.executable, f'{here}/deslop.py', path],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    check(f'{name} non letto come cp1252', r.returncode != 0, 'una pagina piena di segnali è risultata PULITA')
    check(f'{name}: scatta il costrutto', 'costrutto' in r.stdout, r.stdout[:140])
    check(f'{name}: scatta la lineetta', 'lineette' in r.stdout, r.stdout[:140])

_emoji = os.path.join(_dir, 'emoji.html')
with open(_emoji, 'w', encoding='utf-8') as fh:
    fh.write('<p>Un metodo olistico \U0001f338 — unico — per te.</p>')
r = subprocess.run([sys.executable, f'{here}/deslop.py', _emoji],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
check('emoji senza traceback', 'Traceback' not in r.stderr, r.stderr[-160:])
check('emoji: il voto arriva', 'voto' in r.stdout, r.stdout[:140])

# ── un testo umano resta 5/5 ─────────────────────────────────────────────────
for ok in ('Il trattamento dura un’ora e costa 60 euro.',
           'Prima di prenotare, chiamaci: ti diciamo se fa per te.',
           'Non facciamo trattamenti laser. Se ti serve, ti diamo un nome di fiducia.',
           'La consulenza si fa in cabina, con calma, e ti spieghiamo cosa usiamo.'):
    check('testo pulito resta pulito', not groups(ok), f'{ok} -> {groups(ok)}')

# ── Markdown: una citazione non è testo ──────────────────────────────────────
md = markdown_prose('Usa `olistico` qui. Vedi [la guida](u.md) per altro.')
check('codice in linea non valutato', 'olistico' not in md, repr(md))
check('testo del link sopravvive', 'la guida' in md, repr(md))
check('testo intorno sopravvive', 'per altro' in md, repr(md))

md = markdown_prose('> ~~Semplice, veloce ed efficace.~~\n> **Dura un’ora.**')
check('esempio barrato non valutato', 'rhythm' not in groups(md), repr(md))
check('la frase vera sopravvive', 'Dura un' in md, repr(md))

md = markdown_prose('Intro.\n```\nolistico sinergia vero e proprio\n```\nFine.')
check('blocco di codice non valutato', not groups(md), repr(md))

md = markdown_prose('| a | **3/5** — una cosa |\n| b | **5/5** — un’altra cosa |')
check('righe di tabella non si fondono', 'punctuation' not in groups(md), repr(md))

md = markdown_prose('- Fascia 1 — via subito\n- Fascia 2 — di solito via')
check('punti elenco non si fondono', 'punctuation' not in groups(md), repr(md))
md = markdown_prose('- Il nostro staff — formato, attento e vicino — ti aspetta.')
check('lineette dentro un punto elenco scattano ancora', 'punctuation' in groups(md), repr(md))

md = markdown_prose('Se manca un numero, scrivi `[serve un numero]` e vai avanti.')
check('togliere il codice non inventa un elenco a tre', 'rhythm' not in groups(md), repr(md))

md = markdown_prose('Il nostro approccio olistico, intuitivo e innovativo.')
check('Markdown non ammorbidisce il lessico', 'vocab' in groups(md), repr(md))

if fails:
    print(f'{len(fails)} FALLITI\n')
    for f in fails:
        print(f'  · {f}')
    sys.exit(1)
print('tutti i test passano')
