#!/usr/bin/env python3
"""Reproducible orthodox-chess smoke arena, NOT a strength/Elo benchmark."""
import argparse
import pathlib
import chess
import chess.engine
import chess.pgn

p = argparse.ArgumentParser()
p.add_argument("engine")
p.add_argument("--games", type=int, default=4)
p.add_argument("--depth", type=int, default=3)
p.add_argument("--max-plies", type=int, default=80)
p.add_argument("--output", default="sf19-tuning-smoke.pgn")
args = p.parse_args()
assert args.games > 0 and args.games % 2 == 0

engines = [chess.engine.SimpleEngine.popen_uci(args.engine) for _ in range(2)]
try:
    for on, engine in enumerate(engines):
        engine.configure({"Threads": 1, "Hash": 16, "Use NNUE": False, "SF19 Search Tuning": bool(on)})
    results = []
    with open(args.output, "w", encoding="utf8") as out:
        for game_index in range(args.games):
            board = chess.Board()
            # Deterministic symmetric openings for color alternation.
            opening = (game_index // 2) % 2
            for move in (["e2e4", "e7e5"] if opening == 0 else ["d2d4", "d7d5"]):
                board.push_uci(move)
            game = chess.pgn.Game.from_board(board)
            game.headers["Event"] = "SF19 ProbCut exploratory smoke match"
            tuned_color = chess.WHITE if game_index % 2 == 0 else chess.BLACK
            game.headers["White"] = "tuned" if tuned_color else "baseline"
            game.headers["Black"] = "baseline" if tuned_color else "tuned"
            node = game.end()  # from_board() already includes the opening moves
            for ply in range(args.max_plies):
                if board.is_game_over(claim_draw=True):
                    break
                engine = engines[int(board.turn == tuned_color)]
                move = engine.play(board, chess.engine.Limit(depth=args.depth)).move
                if move not in board.legal_moves:
                    raise RuntimeError(f"Illegal move {move} at {board.fen()}")
                board.push(move)
                node = node.add_variation(move)
            outcome = board.outcome(claim_draw=True)
            result = board.result(claim_draw=True) if outcome else "*"
            game.headers["Result"] = result
            print(game, file=out, end="\n\n")
            results.append(result)
            print(f"game {game_index+1}: {result} plies={board.ply()}")
    print(f"Summary (unfinished marked *): {results}")
    print("This is only a short protocol and move-legality match. It cannot establish Elo.")
finally:
    for engine in engines:
        engine.quit()
