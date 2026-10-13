#!/usr/bin/env bash
# deslop-check.sh - AI-slop scanner for Book Genesis prose.
#
#   usage:  tools/deslop-check.sh FILE [FILE ...]   (a directory scans its *.md and *.txt)
#   exit 0 = PASS   exit 1 = FAIL
#
#   tools/deslop-check.sh --caps                      print the calibration table
#
# Rule set: tropes.fyi "AI Writing Tropes" (via the deslopify skill at
# .agents/skills/deslopify/references/style_guide.md), plus the humanizer's list.
#
# THRESHOLDS ARE MEASURED, NOT GUESSED.
# Calibrated against 175,144 words / 48 narrative documents of published prose:
#   Wandering Witch: The Journey of Elaina vols. 1/2/5 (Yen Press). Back matter
#   (afterword/appendix) excluded - it is not fiction.
#   Coldbrook Junction chs. 1-11 (56,144 words) used as a native-English control.
#
# Why Elaina governs and Coldbrook only partly can: Coldbrook writes its dashes as
# "--" and its quotes straight, so it scores 0 em dashes and 0 curly quotes as a
# *formatting* fact, not a style one. It cannot calibrate D1 or A20. It does
# calibrate D2, P1-P3, -ly and every word-level rule.
#
# VALIDATION (tools/calibration/CALIBRATION.md):
#   Elaina, 51 files, 0 failing rows ....... PASS  (human control)
#   Coldbrook, 9/11 published chapters ..... FAIL  (AI-written control)
#   tools/calibration/slop-fixture.md ...... FAIL, 17 rows (positive control)
# A scanner that passes everything is worthless, and one that fails human prose is
# worse. All three controls are re-run by tools/validate-controls.sh whenever these
# caps change - that command is the gate's own check, and it exits nonzero if a
# control misbehaves or a directory scan expands to zero files.
# See tools/calibration/ for the corpus, the measurements and how to re-derive.
#
#   HARD     zero tolerance. Rule only qualifies if it has *zero* occurrences in
#            the calibration corpus. If published prose never does it, it is a tell.
#   DENSITY  published prose does this, so it cannot be banned - only overdone.
#            Cap = ~1.5x the worst single calibration document, so the reference
#            passes with headroom. Caps are rational (n per w words) because
#            integer per-1k math cannot express a limit below 1/1k.
#   PATTERN  algorithmic checks grep cannot do: anaphora, duplication, fragments.
#   NOTE     reported only, never fails - too noisy to judge mechanically.
#
# This proves the mechanical half. Clean-but-voiceless prose is still slop and
# no scanner can see that. Read it aloud too.

set -u

# ---------------------------------------------------------------- calibrated caps
# D1: worst published doc 8.9/1k, p90 6.7, median 3.8  (cap 10, warn 7)
# D2: worst 3.6/1k (cap 5, warn 4)   -ly: worst 24.3/1k (cap 26, warn 20)
# Worst-document rates are from tools/calibration/measure.py; each cap is set at
# roughly 1.5x its worst document so the reference passes with headroom.
OPEN_PER_N=6         # P1 fail: same 2-word opener > 6 times per 1000 words
OPEN_PER_W=1000
OPEN_SHARE_PCT=15    # P1 fail: top opener > 15% of all sentences
DUP_PER_W=2000       # P2 fail above 1 duplicate per 2000 words (min 1 allowed).
                     # Flat "0" was wrong: a published chapter repeats 4 sentences
                     # verbatim as a deliberate refrain. Scaled instead.
# P3 fail at 7+ in a row. Two human documents in the reference corpus reach 6, so 6
# must pass; the slop fixture runs to 9 and still fails. Measured, not chosen.
FRAG_RUN=7

# ---------------------------------------------------------------- tier 1: HARD
# Every pattern below scored ZERO hits in 175,144 words of published narrative.
HARD=(
  'A1a|delve family|(^|[^a-z])(delve|delves|delving|utilize[ds]?|utilizing|streamlin(e|es|ed|ing)|robust|seamless|cutting-edge)([^a-z]|$)'
  'A2a|magic adverbs|(^|[^a-z])(fundamentally|arguably|profoundly|subtly)([^a-z]|$)'
  'A3a|grandiose nouns|(^|[^a-z])(tapestry|paradigm|synergy|ecosystem|myriad|palpable|indelible|intricac(y|ies)|intricate|framework)([^a-z]|$)'
  'A8|false suspense|(here.s the (thing|kicker|catch|problem)|here.s where it gets|here.s what most people)'
  'A10a|nonfiction filler|(it.s worth noting|it bears mentioning|interestingly,|notably,|at its core|due to the fact that)'
  'A11a|signposted close|(in summary|all in all|and so we return)'
  'A12|despite the challenges|despite (these|its|the) (challenges|obstacles|setbacks)'
  'A13|truth-is-simple|(the (reality|truth) is (simple|simpler|clear)|history is (clear|unambiguous)|the evidence is clear)'
  'A14|stakes inflation|(fundamentally reshape|define the next era|something entirely new|change everything|the very nature of)'
  'A15a|analytical -ing|, (highlighting|underscoring|emphasizing|symbolizing|showcasing|signaling|a reminder of)'
  'A16|vague attribution|(experts (say|argue|believe|suggest)|observers (have|noted|say)|industry reports|some critics|many would argue|several publications)'
  'A18|gerund litany|(^|[.!?] )([A-Z][a-z]+ing [^.!?]{0,40}\. ){2,}'
  'A19|listicle in prose|(The (first|second|third|fourth) (wall|takeaway|thing|point|problem|reason) is)'
  'A20|unicode arrows|[→⇒←↔]'
  'A21|chatbot artifact|(I hope this helps|let me know if|great question|as an AI)'
  # NOT a slop rule - a project canon guard. It correctly fires on the excluded
  # book (Coldbrook Junction scores 30 hits here). Zero tolerance is intended.
  # Bare absorb* was removed from this rule: "absorbed in a book" is ordinary
  # English and occurred 4x in the calibration corpus. That sense is now A22b.
  'A22|excluded-book residue|(What the [A-Z][a-z]+ Kept|guest book|a ledger|the ledger)'
)

# -------------------------------------------------------- tier 3: WARN ONLY
# Never fails, never passes silently. Canon-sensitive words a human must rule on.
WARN_ONLY=(
  'A22b|absorption sense (canon guard)|(^|[^a-z])(absorb(ed|s|ing|ption|ptions)?)([^a-z]|$)'
)

# ------------------------------------------------------------- tier 2: DENSITY
# Format: id|name|allow_n|allow_w|warn_n|warn_w|regex     (blank warn = no warn band)
# THE REGEX MUST BE THE LAST FIELD - it contains "|" alternation, so parsing
# from the left would truncate it and produce an unbalanced ( .
# Cap = ~1.5x the worst calibration document; see the trailing comment per row.
DENSITY=(
  'A1b|leverage/harness|1|2000|||(^|[^a-z])(harness(es|ed|ing)?|leverage[ds]?|leveraging)([^a-z]|$)'        # worst 0.31/1k
  'A2b|manner adverbs|2|1000|||(^|[^a-z])(quietly|deeply|remarkably|inevitably|undeniably)([^a-z]|$)'        # worst 0.95/1k
  'A3b|literal nouns|7|1000|||(^|[^a-z])(landscape|realm|vibrant)([^a-z]|$)'                                # worst 4.29/1k
  'A4|serves-as dodge|1|2000|||(serves as|serving as|stands as|standing as|acts as|marking a|represents a|represents an|is a testament)'  # 0.13/1k
  'A5|negative parallelism|2|1000|||(is not|was not|are not|were not|isn.t|wasn.t|aren.t|weren.t|rather than) (just|merely|only|about)'  # 0.61/1k
  'A6|not X not Y|2|1000|||(^|[^a-z])Not [a-z][^.!?]{0,30}\. Not [a-z]'                                    # worst 0.52/1k
  'A7|the X? a Y|1|2000|||(^|[^a-z])The (result|worst part|scary part|problem|answer|truth|catch|kicker)\? '  # 0.12/1k
  'A9|teacher voice|1|2000|||(let.s (break this down|unpack|explore|dive in)|think of it (as|like)|imagine a world where)'  # 0.16/1k
  'A10b|forum filler|2|1000|||(in order to|when it comes to|importantly,)'                                 # worst 1.13/1k
  'A17|invented label|1|2000|||the [a-z]+ (paradox|trap|creep|divide|vacuum|inversion)'                     # 1 hit in 175k ("the one divide")
  'A11b|soft conclusion|1|2000|||(in conclusion|to sum up)'                                                # worst 0.24/1k
  'A15b|participial -ing|3|1000|||, (realizing|knowing|feeling|understanding|reflecting|ensuring|allowing)'  # worst 1.69/1k
  'A23|parenthetical dash|3|1000|||—[^—\n]{1,70}—'                                                         # worst 1.79/1k
  'D1|em dash|10|1000|7|1000|—'                                                                            # worst 8.90/1k
  'D2|rule of three|5|1000|4|1000|[^,.;:]{3,30}, [^,.;:]{3,30}, and [^,.;:]{3,30}'                         # worst 3.58/1k
  'D3|-ly adverbs|26|1000|20|1000|(^|[^a-z])[a-z]{4,}ly([^a-z]|$)'                                         # worst 24.30/1k
)

# ------------------------------------------------------------------ reporting
NOTE_CURLY=1   # curly quotes: typography, not slop. Published books use them
               # (~98/1k). Reported so the .md convention stays visible.

fail=0
warn=0
rate() { awk -v n="$1" -v w="$2" 'BEGIN{ if (w<1) w=1; printf "%.2f", n*1000/w }'; }

print_caps() {
  echo 'DENSITY CAPS - measured from published prose, not chosen'
  echo 'cap = the allowance; warn = the reference median band (a warning, not a defect)'
  echo
  printf '%-5s %-24s %s\n' 'id' 'rule' 'allowance'
  printf '%-5s %-24s %s\n' '-----' '------------------------' '-----------------------------------'
  for entry in "${DENSITY[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; rest=${rest#*|}
    an=${rest%%|*}; rest=${rest#*|}
    aw=${rest%%|*}; rest=${rest#*|}
    wn=${rest%%|*}; rest=${rest#*|}
    if [ -n "$wn" ]; then
      capstr="$an per $aw words (warn above $wn per $aw)"
    else
      capstr="$an per $aw words"
    fi
    printf '%-5s %-24s %s\n' "$id" "$name" "$capstr"
  done
  echo
  echo 'HARD rules (zero tolerance) are the ones with 0 hits in the calibration corpus.'
  exit 0
}

[ "${1:-}" = "--caps" ] && print_caps

scan_file() {
  f="$1"
  words=$(wc -w <"$f" | tr -d ' ')
  [ "$words" -gt 0 ] || words=1
  printf '== %s  (%s words)\n' "$f" "$words"

  for entry in "${HARD[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; re=${rest#*|}
    n=$(grep -oiE "$re" "$f" | wc -l | tr -d ' ')
    if [ "$n" -gt 0 ]; then
      printf '   FAIL  %-5s %-22s x%s  (published prose: 0)\n' "$id" "$name" "$n"
      grep -noiE "$re" "$f" | head -3 | cut -c1-100 | sed 's/^/         /'
      fail=1
    fi
  done

  for entry in "${DENSITY[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; rest=${rest#*|}
    an=${rest%%|*}; rest=${rest#*|}
    aw=${rest%%|*}; rest=${rest#*|}
    wn=${rest%%|*}; rest=${rest#*|}
    ww=${rest%%|*}; rest=${rest#*|}
    re=${rest}
    n=$(grep -oE "$re" "$f" | wc -l | tr -d ' ')
    r=$(rate "$n" "$words")
    if [ $(( n * aw )) -gt $(( an * words )) ]; then
      printf '   FAIL  %-5s %-22s %s per 1k (cap %s/%s)\n' "$id" "$name" "$r" "$an" "$aw"
      fail=1
    elif [ -n "$wn" ] && [ $(( n * ww )) -gt $(( wn * words )) ]; then
      printf '   warn  %-5s %-22s %s per 1k (cap %s/%s)\n' "$id" "$name" "$r" "$an" "$aw"
      warn=1
    else
      printf '   ok    %-5s %-22s %s per 1k (cap %s/%s)\n' "$id" "$name" "$r" "$an" "$aw"
    fi
  done

  # one awk pass for patterns: openers, duplication, fragments
  stats=$(awk '
    { buf = buf $0 " " }
    END {
      gsub(/[.!?] /, "\n", buf)
      n = split(buf, s, "\n")
      nsent = 0; dup = 0; run = 0; best = 0
      for (i = 1; i <= n; i++) {
        line = s[i]
        gsub(/^[^A-Za-z]+/, "", line)
        if (line == "") continue
        nsent++
        m = split(line, w, /[ \t]+/)
        wc = 0
        for (j = 1; j <= m; j++) if (w[j] ~ /[A-Za-z]/) wc++
        if (wc >= 1 && wc <= 4) { run++; if (run > best) best = run } else { run = 0 }
        if (wc >= 2) {
          a = tolower(w[1]); b = tolower(w[2])
          if (a ~ /^[a-z]+$/ && b ~ /^[a-z]+$/) { key = a " " b; cnt[key]++ }
        }
        if (wc >= 8) {
          norm = tolower(line)
          gsub(/[^a-z ]/, "", norm)
          if (length(norm) > 40) {
            if (norm in seen) dup++
            else seen[norm] = 1
          }
        }
      }
      mk = ""
      for (k in cnt) if (mk == "" || cnt[k] > cnt[mk] || (cnt[k] == cnt[mk] && k < mk)) mk = k
      # The opener key is TWO words, so it must come LAST: when it sat in field 4,
      # field 5 held its second word, the fragment-run length was read off it, and
      # P3 could never fire ([ "was" -ge 6 ] is an error, which is false).
      printf "%d %d %d %d %s\n", nsent, (mk == "" ? 0 : cnt[mk]), dup, best, (mk == "" ? "-" : mk)
    }' "$f")
  nsent=$(echo "$stats" | awk '{print $1}')
  mopen=$(echo "$stats" | awk '{print $2}')
  dups=$(echo "$stats" | awk '{print $3}')
  mrun=$(echo "$stats" | awk '{print $4}')
  mkey=$(echo "$stats" | cut -d' ' -f5-)
  [ "$nsent" -gt 0 ] || nsent=1

  share=$(awk -v a="$mopen" -v b="$nsent" 'BEGIN{printf "%.1f", 100*a/b}')
  if [ $(( mopen * OPEN_PER_W )) -gt $(( OPEN_PER_N * words )) ] || awk -v s="$share" -v c="$OPEN_SHARE_PCT" 'BEGIN{exit !(s>c)}'; then
    printf '   FAIL  P1    anaphora abuse          "%s" x%s (%s%% of sentences)\n' "$mkey" "$mopen" "$share"
    fail=1
  else
    printf '   ok    P1    anaphora abuse          "%s" x%s (%s%% of sentences)\n' "$mkey" "$mopen" "$share"
  fi

  dup_allow=$(( words / DUP_PER_W ))
  [ "$dup_allow" -lt 1 ] && dup_allow=1
  if [ "$dups" -gt "$dup_allow" ]; then
    printf '   FAIL  P2    duplicate sentence      %s (allowed %s at %s words)\n' "$dups" "$dup_allow" "$words"
    fail=1
  else
    printf '   ok    P2    duplicate sentence      %s (allowed %s)\n' "$dups" "$dup_allow"
  fi

  if [ "$mrun" -ge "$FRAG_RUN" ]; then
    printf '   FAIL  P3    short-fragment run      %s in a row (cap %s)\n' "$mrun" "$((FRAG_RUN-1))"
    fail=1
  else
    printf '   ok    P3    short-fragment run      %s in a row (cap %s)\n' "$mrun" "$((FRAG_RUN-1))"
  fi

  for entry in "${WARN_ONLY[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; re=${rest#*|}
    n=$(grep -oiE "$re" "$f" | wc -l | tr -d ' ')
    if [ "$n" -gt 0 ]; then
      printf '   warn  %-5s %-22s x%s  (eyeball: excluded-engine sense?)\n' "$id" "$name" "$n"
      warn=1
    fi
  done

  if [ "$NOTE_CURLY" -eq 1 ]; then
    curly=$(grep -oE '[“”‘’]' "$f" | wc -l | tr -d ' ')
    printf '   note  —     curly quotes            %s (typography, not slop; published ~98/1k)\n' "$curly"
  fi
}

for target in "$@"; do
  if [ -d "$target" ]; then
    scanned=0
    for f in "$target"/*.md "$target"/*.txt; do
      [ -f "$f" ] && { scan_file "$f"; scanned=$((scanned+1)); }
    done
    # An empty expansion used to fall through to a vacuous PASS, because nothing
    # ran and "fail" stayed 0. A control that scans zero files proves nothing.
    if [ "$scanned" -eq 0 ]; then
      printf '   FAIL  empty scan: no .md or .txt prose in %s\n' "$target"
      fail=1
    fi
  elif [ -f "$target" ]; then
    scan_file "$target"
  else
    printf 'missing: %s\n' "$target"
    fail=1
  fi
done

echo
if [ "$fail" -eq 0 ] && [ "$warn" -eq 0 ]; then
  echo "RESULT: PASS (mechanical only - read it aloud before calling it clean)"
  exit 0
fi
if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS with warnings - inside every published cap, above the reference median."
  echo "        Warnings are not defects. Read it aloud before calling it clean."
  exit 0
fi
echo "RESULT: FAIL - fix the rows above before this chapter counts as drafted"
exit 1
