"""
Client:
- default: send Propose() to one node (--port)
- optional: send Propose() to all nodes in Constants.PORTLIST[:Constants.N] (--broadcast)
"""

import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import Constants


def send_propose(host: str, port: int, req: helloworld_pb2.PRORequest):
    with grpc.insecure_channel(f"{host}:{port}") as ch:
        stub = helloworld_pb2_grpc.GreeterStub(ch)
        return stub.Propose(req)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=None, help="Send Propose() to a single node port")
    ap.add_argument("--broadcast", action="store_true", help="Send Propose() to all nodes (decentralized start)")
    ap.add_argument("--instance", type=int, default=1)
    ap.add_argument("--value", default="1")
    ap.add_argument("--id", default="client")
    ap.add_argument("--proof", default="")
    args = ap.parse_args()

    req = helloworld_pb2.PRORequest(
        id=args.id,
        instance=args.instance,
        proof=args.proof,
        value=args.value
    )

    if args.broadcast:
        ports = Constants.PORTLIST[: Constants.N]
        print(f"Broadcasting Propose() to {len(ports)} nodes:", ports)
        for p in ports:
            try:
                rep = send_propose(args.host, p, req)
                print(f"Propose reply from {p}: {rep}")
            except Exception as e:
                print(f"Propose failed to {p}: {e}")
        return

    if args.port is None:
        raise SystemExit("Either provide --port (single node) or use --broadcast.")

    rep = send_propose(args.host, args.port, req)
    print("Propose reply:", rep)


if __name__ == "__main__":
    main()