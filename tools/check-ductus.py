#!/usr/bin/env python3
"""check-ductus.py - the per-book voice carryover check.

A book assigned to a ductus must leave a log a fresh session can read: one entry
per chapter, naming the contract digest and the tone/register the chapter was
drafted to preserve. This wrapper runs `ductus.py audit` and preserves its exit
codes, so run-gates can treat a missing log as a hygiene failure rather than a
prose judgement.

Exit: 0 pass, 1 fail, 2 not run / no chapters / unassigned, 3 no YAML.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "ductus.py")


def main():
    if len(sys.argv) != 2:
        print("usage: python tools/check-ductus.py <book-root>")
        return 2
    proc = subprocess.run([sys.executable, TOOL, "audit", sys.argv[1]],
                          capture_output=True, text=True)
    sys.stdout.write(proc.stdout or "")
    sys.stderr.write(proc.stderr or "")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
