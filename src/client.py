# src/client.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # allow imports from repo root

import argparse
import grpc
from proto import helloworld_pb2
from proto import helloworld_pb2_grpc
from config import constants as Constants

def send_one(host: str, port: int, inst: int, value: str, timeout_s: float = 2.0):
    with grpc.insecure_channel(f"{host}:{port}") as ch:
        stub = helloworld_pb2_grpc.GreeterStub(ch)
        req = helloworld_pb2.PRORequest(id="client", type="", instance=inst, proof="", value=value)
        return stub.Propose(req, timeout=timeout_s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=50054)
    ap.add_argument("--broadcast", action="store_true")
    ap.add_argument("--instance", type=int, default=1)
    ap.add_argument("--value", default="1")
    args = ap.parse_args()

    ports = Constants.PORTLIST[: getattr(Constants, "N", len(Constants.PORTLIST))]

    if not args.broadcast:
        rep = send_one(args.host, args.port, args.instance, args.value)
        print(f"Propose reply from {args.port}: {rep}", flush=True)
        return

    print(f"Broadcasting Propose() to {len(ports)} nodes: {ports}", flush=True)
    for p in ports:
        try:
            rep = send_one(args.host, p, args.instance, args.value)
            print(f"Propose reply from {p}: {rep}", flush=True)
        except Exception as e:
            print(f"Propose FAILED to {p}: {e}", flush=True)

if __name__ == "__main__":
    main()