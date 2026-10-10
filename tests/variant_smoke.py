#!/usr/bin/env python3
"""Minimal cross-variant smoke; fuller perft suites and match tests still required."""
import sys
from uci_smoke import check_engine
for variant in ("chess", "janggi", "xiangqi", "shogi", "crazyhouse"):
    check_engine(sys.argv[1], variant)

# Actually search with experimental orthodox-only tuning enabled.
check_engine(sys.argv[1], 'chess', sf19_tuning=True)
