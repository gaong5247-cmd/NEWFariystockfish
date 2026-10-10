# Dual NNUE UCI frontend (experimental)

Launch `python3 tools/dual_nnue_uci.py` from the repository root after compiling both engine binaries and obtaining the official SF19 network in `networks/nn-1a298aa575a0.nnue`.

Override paths with `FAIRY_ENGINE`, `SF19_ENGINE`, `SF19_NET` or flags `--fairy`, `--sf19`, `--net`.

UCI options:

- `setoption name NNUEBackend value Fairy`: Fairy search with Fairy legacy variant-aware evaluation.
- `setoption name NNUEBackend value Stockfish19`: Stockfish 19 search with its official SFNNv16 evaluation (**orthodox chess only**).
- `setoption name UCI_Variant value janggi`: Fairy variants. Switch to Fairy before selecting a non-chess variant.
- `setoption name FairyEvalFile value /path/to/variant.nnue`: Legacy Fairy NNUE path.
- `setoption name Use NNUE value true`: Enable Fairy's native NNUE if a compatible network is installed. Default is false for the proxy's portable smoke behavior.

Sample:

```text
uci
setoption name NNUEBackend value Stockfish19
isready
position startpos
go depth 8
```

**Architecture limitation:** This is an **engine dispatcher**, not two interchangeable NNUE evaluators used inside the same Fairy alpha-beta search. To integrate SFNNv16 into Fairy search, SF19 feature extraction, accumulator management and ABI must still be ported to Fairy's board representation, with careful evaluation validation. Neither SF19 SFNNv16 weights nor the standard chess feature transformer can score Janggi/Xiangqi/Shogi positions without separately trained compatible networks.

The script is experimental and intended for smoke testing; asynchronous UCI command transitions should be tested with the target GUI, especially switching backends during searches. It is not yet a production-ready engine binary or proof of Elo gain.
