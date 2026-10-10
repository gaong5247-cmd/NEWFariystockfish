#!/usr/bin/env python3
"""Dual NNUE UCI frontend: Fairy legacy NNUE or official SF19 SFNNv16 runtime.

SF19 mode delegates SEARCH AND EVALUATION to upstream Stockfish 19.
Fairy mode delegates both to Fairy Stockfish. It does NOT inject SFNNv16
evaluation inside Fairy's search; this limitation is intentionally explicit.
"""
import argparse
import os
import pathlib
import queue
import subprocess
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[1]

def spawn(path):
    if not path.is_file():
        raise RuntimeError(f"Engine binary not found: {path}")
    return subprocess.Popen([str(path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=sys.stderr, text=True, bufsize=1)

class Proxy:
    def __init__(self, fairy, sf19, net):
        self.paths = {"Fairy": pathlib.Path(fairy).resolve(),
                      "Stockfish19": pathlib.Path(sf19).resolve()}
        self.net = pathlib.Path(net).resolve()
        self.backend = "Fairy"
        self.variant = "chess"
        self.fairy_net = None
        self.handshaking = True
        self.engine = None
        self.events = queue.Queue()
        self.generation = 0
        self.position = "position startpos"
        self.options = {"Threads": "1", "Hash": "16"}
        self.start()

    def start(self):
        if self.backend == "Stockfish19" and self.variant != "chess":
            raise RuntimeError("Stockfish 19 NNUE supports orthodox chess only")
        self.handshaking = True
        self.stop()
        self.engine = spawn(self.paths[self.backend])
        self.generation += 1
        generation = self.generation
        def pump():
            for line in self.engine.stdout:
                output = line.rstrip("\n")
                if generation == self.generation and not self.handshaking:
                    print(output, flush=True)
                else:
                    self.events.put((generation, output))
        threading.Thread(target=pump, daemon=True).start()
        self.send("uci")
        self.until("uciok")
        for k, v in self.options.items():
            self.send(f"setoption name {k} value {v}")
        if self.backend == "Fairy":
            self.send(f"setoption name UCI_Variant value {self.variant}")
            if self.fairy_net:
                self.send(f"setoption name EvalFile value {self.fairy_net}")
        else:
            if not self.net.is_file():
                raise RuntimeError(f"Missing Stockfish 19 SFNNv16 net: {self.net}")
            self.send(f"setoption name EvalFile value {self.net}")
        self.send("isready")
        self.until("readyok")
        self.send(self.position)
        self.handshaking = False

    def until(self, target):
        import time
        end = time.monotonic() + 25
        while time.monotonic() < end:
            try:
                generation, line = self.events.get(timeout=.3)
            except queue.Empty:
                continue
            if generation == self.generation and line == target:
                return
        raise RuntimeError(f"{self.backend} did not respond: {target}")

    def send(self, command):
        self.engine.stdin.write(command + "\n")
        self.engine.stdin.flush()

    def stop(self):
        if self.engine:
            try:
                self.send("quit")
                self.engine.wait(timeout=3)
            except (OSError, subprocess.TimeoutExpired):
                self.engine.kill()
                self.engine.wait()
            self.engine = None

    def handle(self, line):
        if line == "uci":
            print("id name NEW Fairy SF19 Dual NNUE Frontend", flush=True)
            print("id author NEWFariystockfish contributors", flush=True)
            print("option name NNUEBackend type combo default Fairy var Fairy var Stockfish19", flush=True)
            print("option name UCI_Variant type string default chess", flush=True)
            print("option name FairyEvalFile type string default <empty>", flush=True)
            print("option name Threads type spin default 1 min 1 max 512", flush=True)
            print("option name Hash type spin default 16 min 1 max 33554432", flush=True)
            print("uciok", flush=True)
            return True
        if line.startswith("setoption name "):
            body = line[len("setoption name "):]
            name, sep, value = body.partition(" value ")
            if name == "NNUEBackend":
                if value not in self.paths:
                    print(f"info string Unsupported NNUEBackend {value}", flush=True)
                elif value == "Stockfish19" and self.variant != "chess":
                    print("info string SF19 only supports chess; select chess first", flush=True)
                else:
                    self.backend = value
                    self.start()
            elif name == "UCI_Variant":
                if self.backend == "Stockfish19" and value != "chess":
                    print("info string SF19 cannot evaluate this variant; select Fairy first", flush=True)
                else:
                    self.variant = value
                    self.position = "position startpos"
                    self.start()
            elif name == "FairyEvalFile":
                self.fairy_net = value if value != "<empty>" else None
                if self.backend == "Fairy":
                    self.start()
            elif name in self.options:
                self.options[name] = value
                self.send(line)
            else:
                self.send(line)
            return True
        if line == "isready":
            self.handshaking = True
            self.send(line)
            self.until("readyok")
            self.handshaking = False
            print("readyok", flush=True)
            return True
        if line.startswith("position "):
            self.position = line
            self.send(line)
            return True
        if line == "ucinewgame":
            self.position = "position startpos"
            self.send(line)
            return True
        if line == "quit":
            return False
        self.send(line)
        return True

    def run(self):
        try:
            for line in sys.stdin:
                # Drain lines from current engine for live info/bestmove.
                self.flush()
                if not self.handle(line.strip()):
                    break
                self.flush()
        finally:
            self.stop()

    def flush(self):
        while True:
            try:
                generation, line = self.events.get_nowait()
            except queue.Empty:
                break
            if generation == self.generation and not line.startswith(("id ", "option ", "uciok", "readyok")):
                print(line, flush=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fairy", default=os.environ.get("FAIRY_ENGINE", str(ROOT / "src/stockfish")))
    p.add_argument("--sf19", default=os.environ.get("SF19_ENGINE", str(ROOT / "vendor/stockfish19/src/stockfish")))
    p.add_argument("--net", default=os.environ.get("SF19_NET", str(ROOT / "networks/nn-1a298aa575a0.nnue")))
    args = p.parse_args()
    Proxy(args.fairy, args.sf19, args.net).run()

if __name__ == "__main__":
    main()
