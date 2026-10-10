# Stockfish 19 modernization checklist

**Baseline:** Fairy-Stockfish 14 (2021), not a direct Stockfish 19 fork. Verify compatibility before each port.

| Phase | Candidate | Risk | Required tests |
| --- | --- | --- | --- |
| 0 | Import upstream + make baseline builds | Low | CI compile, variant smoke, perft |
| 1 | TT/history/correction history exploration | Medium | reproducible node counts and tactical suites |
| 2 | Better move ordering and reductions | High | non-chess perft, search stability, Elo SPRT |
| 3 | Search extensions, futility/null pruning | Very high | zugzwang, drops, check rules, Xiangqi and Janggi |
| 4 | NNUE evaluation infrastructure | Very high | variant feature compatibility; net serialization |
| 5 | platform optimization | Medium | x64 and ARM64 benchmarks |

## Variant-specific danger points

- **Janggi:** pass moves, palace-specific moves, legal states, repetition and scoring. Do not assume western chess's checks/terminal rules.
- **Xiangqi:** facing generals, cannon and horse movement, 9×10 representation.
- **Shogi / crazyhouse:** drops and hand-piece counts invalidate common chess pruning intuition.
- **Losing chess / racing kings:** chess evaluation assumptions and normal check semantics may not apply.
- **Different board dimensions:** feature indexing, bitboards and SIMD assumptions need separate validation.

## Engineering rules

- Maintain a baseline executable and pin toolchain/settings.
- Keep each Stockfish-derived port in a standalone commit with source commit noted.
- Avoid copying `src/search.cpp`, `src/position.cpp` or SFNNv16 `nnue` wholesale.
- Measure improvements against upstream Fairy-Stockfish at the **same variant** and settings; comparing to standard Stockfish 19 in chess alone does not demonstrate strength on Janggi.
- Run complete GPL license checks for redistributed source/binaries.

## Proposed first patch after import

Add repeatable test harness for `chess`, `janggi`, `xiangqi`, `shogi`, and `crazyhouse` and an NPS/depth benchmark; then implement one bounded search improvement at a time.
