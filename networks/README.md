# Stockfish 19 NNUE acquisition

The official **Stockfish 19 (sf_19)** default neural-network weights file is:

`nn-1a298aa575a0.nnue` (SFNNv16; roughly 94 MB).

Official source: https://tests.stockfishchess.org/api/nn/nn-1a298aa575a0.nnue

## Fetching

Use **Actions → Obtain Stockfish 19 NNUE → Run workflow** and download the artifact `stockfish19-sfnnv16-network`. The workflow downloads the original network, verifies the SHA-256 prefix `1a298aa575a0`, and includes the complete SHA256SUMS output. Artifacts expire after 30 days.

Alternatively, `make -C vendor/stockfish19/src net` uses Stockfish's official build-system downloader.

## Important compatibility notice

These are **Stockfish 19 SFNNv16 weights**, not a Fairy-Stockfish 14 NNUE network. Merely downloading them or changing the Fairy 14 `EvalFile` setting **does not** make the old Fairy evaluator compatible with them.

- Keep Fairy-specific networks for Janggi, Xiangqi, Shogi and other variants.
- To use SF19 weights, a real SFNNv16 runtime (feature extraction, accumulator and network loader) must be integrated and validated.
- Never silently reinterpret one network format as the other.
- Until the backend is integrated, run Stockfish 19 as a separate reference engine to evaluate standard chess.
- The official networks repository identifies these weights as CC0, while the engine itself is GPLv3 or later.

Reference: https://github.com/official-stockfish/networks
