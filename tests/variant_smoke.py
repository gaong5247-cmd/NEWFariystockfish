#!/usr/bin/env python3
"""Minimal cross-variant smoke; fuller perft suites and match tests still required."""
import sys
from uci_smoke import check_engine
for variant in ("chess", "janggi", "xiangqi", "shogi", "crazyhouse"):
    check_engine(sys.argv[1], variant)

# Exercise experimental SF19 ProbCut branch on orthodox chess.
import subprocess
p = subprocess.run([sys.argv[1]], input=(
    "uci\nsetoption name Use NNUE value false\n"
    "setoption name SF19 Search Tuning value true\n"
    "isready\nposition startpos\ngo depth 3\nquit\n"),
    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=40)
assert "option name SF19 Search Tuning" in p.stdout, p.stdout
assert p.returncode == 0, p.stdout
print("PASS SF19 UCI tuning option")
