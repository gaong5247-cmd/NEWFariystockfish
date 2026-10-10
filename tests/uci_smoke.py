#!/usr/bin/env python3
"""Protocol smoke tests. Tests boot and bestmove output, not Elo or rules correctness."""
import subprocess
import sys
import threading
import queue

def check_engine(path, variant, sf19_tuning=False):
    process = subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, bufsize=1)
    messages = queue.Queue()
    def reader():
        for line in process.stdout:
            messages.put(line.strip())
    threading.Thread(target=reader, daemon=True).start()
    def send(command):
        process.stdin.write(command + "\n")
        process.stdin.flush()
    def until(test, timeout=25):
        import time
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try: line = messages.get(timeout=max(.01, min(.5, end-time.monotonic())))
            except queue.Empty: continue
            if test(line): return line
        raise RuntimeError(f"Timeout waiting for engine ({variant})")
    try:
        send("uci")
        until(lambda s: s == "uciok")
        send("setoption name Threads value 1")
        if sf19_tuning:
            send("setoption name SF19 Search Tuning value true")
        send("setoption name Use NNUE value false") if variant != "sf19" else None
        if variant not in ("sf19", "chess"):
            send(f"setoption name UCI_Variant value {variant}")
        send("isready")
        until(lambda s: s == "readyok")
        send("position startpos")
        if variant != "sf19":
            send("d")
            fen_line = until(lambda line: line.startswith("Fen: "))
            fen = fen_line.removeprefix("Fen: ").split(" ")[0]
            standard = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
            if variant in ("janggi", "xiangqi", "shogi") and fen == standard:
                raise RuntimeError(f"{variant}: variant did not switch away from chess start FEN")
            print(f"POSITION {variant}: {fen}")
        send("go depth 2")
        move = until(lambda s: s.startswith("bestmove "), timeout=45)
        if move == "bestmove (none)":
            raise RuntimeError(f"No move for {variant}")
        print(f"PASS {variant}: {move}")
    finally:
        try: send("quit")
        except (BrokenPipeError, OSError): pass
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill()

if __name__ == "__main__":
    check_engine(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "chess")
