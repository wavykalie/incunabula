"""Pre-flight verifier for outline.md. Parses ONLY the four Act chapter tables.

Deliberately not a regex over the whole file: the clue-ledger table has the same
row shape and a whole-file scan silently merges the two. That bug produced a
nonsense 77% CV and a bogus 'adjacent identical' once already.
"""
import io, re, sys, statistics as st

path = sys.argv[1] if len(sys.argv) > 1 else 'outline.md'
text = io.open(path, encoding='utf-8').read()
head = text.split('## The 15-item fair-play clue ledger')[0]

rows = []
for line in head.splitlines():
    m = re.match(r'^\|\s*(\d+)\s*\|(.*)$', line)
    if not m:
        continue
    cells = [c.strip() for c in m.group(2).split('|')]
    if len(cells) < 3 or not cells[1].replace(',', '').isdigit():
        continue
    rows.append((int(m.group(1)), cells[0], int(cells[1].replace(',', '')), cells[2]))

fails = []
def check(ok, label, detail):
    print(('  PASS  ' if ok else '  FAIL  ') + label + '  ' + detail)
    if not ok:
        fails.append(label)

print('outline pre-flight:', path)
ns = [r[0] for r in rows]
ws = [r[2] for r in rows]
stc = [r[3] for r in rows]
cv = st.pstdev(ws) / st.mean(ws) * 100

check(len(rows) == 30, '30 chapter rows', 'got %d' % len(rows))
check(ns == list(range(1, 31)), 'contiguous 1-30', 'got %s' % (ns if ns != list(range(1, 31)) else 'ok'))
check(80000 <= sum(ws) <= 95000, 'sum within declared 80,000-95,000', 'sum %d' % sum(ws))
check(33.4 <= cv <= 45.1, 'CV in published-fiction band 33.4-45.1', 'CV %.2f%%' % cv)
check(min(ws) >= 1200, 'no chapter under 1,200 (catchword needs hook+pull)', 'min %d' % min(ws))
adj = [ns[i] for i in range(1, len(ns)) if stc[i] == stc[i-1]]
check(not adj, 'no adjacent-identical structures', 'dupes at %s' % adj if adj else '0 of 29 boundaries')
check(len(set(stc)) >= 8, '>=8 distinct structures', '%d' % len(set(stc)))
led = text.split('## The 15-item fair-play clue ledger')[1]
items = re.findall(r'^\|\s*(\d+)\s*\|', led, re.M)
check([int(i) for i in items] == list(range(1, 16)), 'ledger 1-15 contiguous', 'got %s' % items)

print()
print('mean %.0f  min %d  max %d  ratio %.2fx' % (st.mean(ws), min(ws), max(ws), max(ws)/min(ws)))
print(('ALL CHECKS PASS' if not fails else 'FAILURES: ' + ', '.join(fails)))
sys.exit(1 if fails else 0)
