#!/usr/bin/env bash
# La pulizia col modello rivale: un secondo modello toglie i segnali che il primo ha scritto.
#
# La regola: la pulizia la fa una famiglia di modelli DIVERSA da quella che ha scritto
# la bozza. Un modello sente male il proprio accento, uno rivale lo sente subito.
#
#   ./cleanse.sh bozza.md                # pulisce un file
#   cat bozza.md | ./cleanse.sh -        # pulisce lo standard input
#   TIMEOUT=240 ./cleanse.sh bozza.md    # più tempo per un documento lungo
#
# Chi pulisce, in quest'ordine:
#   1. c'è codex e DESLOP_WRITER non è gpt  -> passaggio GPT con `codex exec`
#   2. c'è claude e DESLOP_WRITER=gpt       -> passaggio Claude con `claude -p`
#   3. nessuno dei due                      -> stampa il prompt da incollare nella chat rivale
#
# Esce sempre con 124 se scade il tempo. Ricontrolla SEMPRE il risultato:
#   python3 tools/deslop.py pulito.md
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$HERE/../prompts/cleanse.txt"
TIMEOUT="${TIMEOUT:-180}"

if [ "${1:-}" = "-" ] || [ $# -eq 0 ]; then
  DRAFT="$(cat)"
else
  # Senza questo controllo un nome di file sbagliato mandava una bozza VUOTA al
  # modello e scriveva la risposta nel file d'uscita con codice 0.
  [ -f "$1" ] && [ -r "$1" ] || { echo "cleanse: impossibile leggere $1" >&2; exit 66; }
  DRAFT="$(cat "$1")"
fi
[ -n "$(printf '%s' "$DRAFT" | tr -d '[:space:]')" ] || {
  echo "cleanse: la bozza è vuota, niente da pulire" >&2; exit 66; }

FULL="$(cat "$PROMPT_FILE")

$DRAFT"

find_bin() { command -v "$1" 2>/dev/null || { [ -x "$HOME/.local/bin/$1" ] && echo "$HOME/.local/bin/$1"; }; }

# La risposta è: il testo, una riga marcatore, le note. Il testo va sullo STDOUT, così
# `cleanse.sh bozza.md > pulito.md` scrive solo il testo; le note vanno sullo STDERR.
#
# Il marcatore non è `---`: `---` è una riga orizzontale Markdown e il delimitatore del
# frontmatter YAML, e tagliare lì troncava ogni bozza che ne conteneva uno.
#
# Senza marcatore si sbaglia dalla parte del testo: tutto esce come testo, con un
# avviso. Una nota in più la vedi e la togli; un paragrafo mangiato no.
NOTES_SENTINEL='<<<SLOPMONSTER-NOTES>>>'

emit_copy() {
  awk -v s="$NOTES_SENTINEL" '
    $0 == s { seen = 1; next }
    seen    { notes = notes $0 "\n"; next }
            { body = body $0 "\n" }
    END {
      if (!seen) {
        printf "%s", body
        print "cleanse: ATTENZIONE nella risposta manca la riga " s "." > "/dev/stderr"
        print "cleanse: esce tutto come testo. Controlla la fine prima di pubblicare," > "/dev/stderr"
        print "cleanse: perché le note del modello potrebbero essere finite nel testo." > "/dev/stderr"
        exit 0
      }
      sub(/\n+$/, "", body)          # via le righe vuote prima del marcatore
      printf "%s\n", body
      if (notes != "") {
        print ""                         > "/dev/stderr"
        print "cleanse: cosa è cambiato -" > "/dev/stderr"
        printf "%s", notes               > "/dev/stderr"
      }
    }
  '
}

CODEX="$(find_bin codex || true)"
CLAUDE="$(find_bin claude || true)"

run_bounded() {  # run_bounded <cmd...>  — macOS non ha `timeout`, quindi ce lo facciamo
  OUT="$(mktemp)"; trap 'rm -f "$OUT"' RETURN
  "$@" >"$OUT" 2>&1 </dev/null &
  PID=$!; WAITED=0
  while kill -0 "$PID" 2>/dev/null; do
    if [ "$WAITED" -ge "$TIMEOUT" ]; then
      kill -9 "$PID" 2>/dev/null; wait "$PID" 2>/dev/null
      echo "cleanse: tempo scaduto dopo ${TIMEOUT}s" >&2; return 124
    fi
    sleep 2; WAITED=$((WAITED + 2))
  done
  wait "$PID"; RC=$?; cat "$OUT"; return $RC
}

if [ -n "$CODEX" ] && [ "${DESLOP_WRITER:-claude}" != "gpt" ]; then
  # Ha scritto Claude (o Gemini) -> pulisce GPT.
  # -o scrive solo l'ultimo messaggio in un file: niente intestazioni da ritagliare.
  # Sandbox in sola lettura: è una trasformazione di testo, non deve scrivere file.
  LAST="$(mktemp)"; trap 'rm -f "$LAST"' EXIT
  LOG="$(run_bounded "$CODEX" exec --skip-git-repo-check --sandbox read-only -o "$LAST" "$FULL")" || {
    RC=$?; printf '%s\n' "$LOG" | tail -20 >&2; exit $RC; }
  if [ -s "$LAST" ]; then
    emit_copy <"$LAST"
  else
    echo "cleanse: codex non ha restituito nessun messaggio" >&2
    printf '%s\n' "$LOG" | tail -20 >&2; exit 1
  fi
elif [ -n "$CLAUDE" ] && [ "${DESLOP_WRITER:-claude}" = "gpt" ]; then
  # Ha scritto GPT -> pulisce Claude.
  # Catturato prima di dividerlo, non in pipe: una pipe restituisce il codice
  # dell'ULTIMO comando, e il 124 del tempo scaduto andrebbe perso.
  CLAUDE_OUT="$(run_bounded "$CLAUDE" -p "$FULL")" || exit $?
  printf '%s\n' "$CLAUDE_OUT" | emit_copy
else
  # Qui si arriva quando l'unica CLI disponibile è della stessa famiglia che ha
  # scritto la bozza: sarebbe un modello che corregge il proprio compito, cioè
  # l'unica cosa che questo script esiste per evitare. Stampa il prompt.
  echo "cleanse: nessuna CLI della famiglia rivale (una bozza di Claude vuole codex," >&2
  echo "una bozza di GPT vuole claude). Incolla il blocco qui sotto nella chat dell'altra famiglia:" >&2
  echo >&2
  printf '%s\n' "$FULL"
  exit 127
fi
