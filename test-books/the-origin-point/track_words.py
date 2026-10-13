"""Per-chapter word tracker. Counts the way the gate counts: len(text.split()).

Written after ch-01 came in 819 words under its 3,200 target and the only reason
I noticed was an ad-hoc shell loop that also printed a stray line. A check that
only runs when someone remembers to run it is not a check.

Targets are read from outline.md, so the tracker and the outline cannot drift
apart. Chapter headings are stripped before counting, matching the gate's
whole-file tokenisation closely enough to keep the two from disagreeing by
double digits.

Usage:
    python track_words.py            # report only
    python track_words.py --strict   # exit 1 if any written chapter is >12% under
"""
import io, os, re, sys, statistics as st

ROOT = os.path.dirname(os.path.abspath(__file__))
CH_DIR = os.path.join(ROOT, 'manuscript', 'chapters')
TOLERANCE = 0.12  # book 1 finished +0.5% over a *floor*; here we guard the floor

def load_targets():
    text = io.open(os.path.join(ROOT, 'outline.md'), encoding='utf-8').read()
    head = text.split('## The 15-item fair-play clue ledger')[0]
    out = {}
    for line in head.splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|(.*)$', line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split('|')]
        if len(cells) < 3 or not cells[1].replace(',', '').isdigit():
            continue
        out[int(m.group(1))] = (cells[0], int(cells[1].replace(',', '')))
    return out

def count(path):
    t = io.open(path, encoding='utf-8').read()
    t = re.sub(r'^#.*$', '', t, flags=re.M)          # drop the heading line
    return len(t.split())

def main():
    targets = load_targets()
    if not targets:
        print('no targets parsed from outline.md')
        return 1
    written, rows = {}, []
    if os.path.isdir(CH_DIR):
        for fn in sorted(os.listdir(CH_DIR)):
            # chapter-NN.md, not ch-NN.md. The gates glob for `chapter[-_ ]?\d+`; a book
            # whose files are named ch-NN.md is invisible to all six of them, and they exit
            # non-zero rather than reporting a false pass - which is correct, and easy to
            # misread as "the gates are broken" rather than "the book was never checked".
            m = re.match(r'chapter-(\d+)\.md$', fn)
            if m:
                written[int(m.group(1))] = os.path.join(CH_DIR, fn)

    print('%-6s %-28s %7s %7s %8s' % ('ch', 'title', 'target', 'actual', 'delta'))
    print('-' * 60)
    under = []
    for n in sorted(targets):
        title, tgt = targets[n]
        if n not in written:
            continue
        a = count(written[n])
        d = a - tgt
        pct = d / tgt * 100.0
        flag = ''
        if pct < -TOLERANCE * 100:
            flag = '  <-- UNDER'
            under.append(n)
        print('%-6d %-28s %7d %7d %+8d  %+6.1f%%%s'
              % (n, title[:28], tgt, a, d, pct, flag))

    done = sorted(written)
    print('-' * 60)
    if not done:
        print('no chapters written yet')
        return 0
    actuals = [count(written[n]) for n in done]
    total_t = sum(targets[n][1] for n in done)
    total_a = sum(actuals)
    print('written %d/%d chapters · %d words against %d targets (%+.1f%%)'
          % (len(done), len(targets), total_a, total_t,
             (total_a - total_t) / total_t * 100.0))
    print('projected full book at current rate: %d words (contract 80,000-95,000)'
          % round(total_a / len(done) * len(targets)))
    print('chapter-length CV so far: %.2f%% (band 33.4-45.1)'
          % (st.pstdev(actuals) / st.mean(actuals) * 100.0))
    if under:
        print('UNDER TOLERANCE: chapters %s' % under)
    if '--strict' in sys.argv and under:
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
