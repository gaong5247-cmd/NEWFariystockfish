# NEW Fairy-Stockfish — SF19 Modernization

A staged modernization of [Fairy-Stockfish](https://github.com/fairy-stockfish/Fairy-Stockfish) 14 toward search and evaluation techniques used in [Stockfish 19](https://github.com/official-stockfish/Stockfish/releases/tag/sf_19).

> **Status:** Bootstrap and migration planning only. No claim of Stockfish 19 playing strength, ported search changes, or proven Elo gain.

## Start here

This repository starts empty by design. To import the audited upstream baseline:

1. Open **Actions → Import Fairy-Stockfish 14 baseline → Run workflow**.
2. Choose `fairy_sf_14` (exact 14.0 baseline), or `fairy_sf_14_0_1_xq` (14.0.1 Xiangqi/Janggi NNUE release).
3. The workflow downloads the official source, retains the upstream GPL license, and commits it to this repo. The import **refuses to overwrite an existing `src/search.cpp`**.
4. Build and benchmark the imported baseline before tuning.

**Important:** The source release and its downloadable prebuilt binaries are not necessarily identical artifacts. Some NNUE networks are supplied in specific release packages. Validate `EvalFile` and variant options when shipping engine binaries.

## Porting strategy

1. **Baseline and correctness:** UCI/UCCI/USI, variant move legality, perft, board sizes, castling, checks, repetition, hand/drop moves, terminal evaluation.
2. **Search correctness:** move ordering, TT and history, quiescence, aspiration, fail-soft search. Port narrowly scoped SF19 ideas instead of replacing variant-aware files wholesale.
3. **Pruning tuning:** LMR, null move, futility/reverse futility, singular extensions. Disable or specialize heuristics for variants where assumptions fail.
4. **Evaluation:** preserve variant-aware NNUE feature encodings. SFNNv16 is *not* plug-compatible with Fairy 14 or non-chess boards.
5. **Performance:** benchmark standard and large-board targets on x86-64 and ARM64; investigate SIMD and thread contention only after correctness.

## Acceptance criteria (not yet verified)

- Every existing supported variant still parses initial positions and performs legal move generation.
- Perft matches a trusted baseline at several depths for representative variants.
- UCI reports `bestmove` with no crashes under fixed depth/time controls.
- Match results use alternating colors/openings, equal hardware and network files, and report W/D/L + confidence intervals.
- No Elo / NPS improvement claims until measured.

## Provenance and licensing

Original Fairy-Stockfish copyright remains with its contributors. GPL-3.0 terms apply to the imported source and distributed derivatives. Preserve copyright notices and `Copying.txt`. Contributions derived from official Stockfish must respect its GPL requirements.

See [MIGRATION.md](MIGRATION.md) for the implementation checklist.
