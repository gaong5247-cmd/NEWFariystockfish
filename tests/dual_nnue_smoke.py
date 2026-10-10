#!/usr/bin/env python3
import pathlib
import queue
import subprocess
import sys
import threading
import time

cmd = [sys.executable, "tools/dual_nnue_uci.py"]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT, text=True, bufsize=1)
q = queue.Queue()
threading.Thread(target=lambda: [q.put(line.strip()) for line in p.stdout], daemon=True).start()

def send(msg):
    p.stdin.write(msg + "\n")
    p.stdin.flush()

def until(prefix, timeout=45):
    end = time.monotonic() + timeout
    seen = []
    while time.monotonic() < end:
        try:
            s = q.get(timeout=.5)
        except queue.Empty:
            if p.poll() is not None:
                raise AssertionError(f"Exited early: {seen}")
            continue
        seen.append(s)
        if s.startswith(prefix):
            return s
    raise AssertionError(f"Timeout {prefix}: {seen[-15:]}")

try:
    send("uci")
    until("option name NNUEBackend")
    until("uciok")
    send("setoption name Use NNUE value false")
    send("position startpos")
    send("go depth 2")
    print("Fairy:", until("bestmove "))
    send("setoption name NNUEBackend value Stockfish19")
    send("isready")
    until("readyok")
    send("position startpos")
    send("go depth 2")
    print("SF19:", until("bestmove "))
    send("setoption name NNUEBackend value Fairy")
    send("setoption name UCI_Variant value janggi")
    send("setoption name Use NNUE value false")
    send("isready")
    until("readyok")
    send("position startpos")
    send("go depth 2")
    print("Janggi:", until("bestmove "))
finally:
    send("quit")
    p.wait(timeout=10)
