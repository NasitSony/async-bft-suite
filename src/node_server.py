# greeter_server.py
"""
Common gRPC node server for your async-BFT protocol suite.

- Each node runs ONE server instance.
- Other nodes call RPC methods (VCBC/ABBA/Propose/Recommend/etc).
- Server replies only with the RPC reply message (protobuf defaults OK).
- Protocol "real actions" (sending more messages) should be triggered via this node's client layer
  (outside this handler), not via the reply.
"""

from __future__ import annotations

import argparse
import logging
from concurrent import futures
from typing import Optional

import grpc

import helloworld_pb2 as pb
import helloworld_pb2_grpc as pb_grpc
from protocol.pmvba import PMVBAProtocol


# -----------------------------
# Protocol handlers (plug-ins)
# -----------------------------
class ProtocolHandlers:
    """
    Plug your real implementations here.
    For now, these just log and return empty replies (valid proto3 defaults).

    """

    def __init__(self, node_id: int, peers: list[int], f: int, node_client):
    self.node_id = node_id
    self.node_client = node_client

    # convert peer ids to string (because proto uses string id)
    peer_ids = [str(p) for p in peers]

    self.pmvba = PMVBAProtocol(
        node_id=str(node_id),
        peers=peer_ids,
        f=f,
        send_propose=lambda peer, req: self.node_client.propose(peer, req),
        send_reco=lambda peer, req: self.node_client.recommend(peer, req),
    )

    # ---- Greeter service RPCs ----
    def vcbc(self, request: pb.VCBCRequest, variant: str) -> pb.VCBCReply:
        logging.info("[%s] VCBC from=%s inst=%s", variant, getattr(request, "id", "?"), getattr(request, "instance", "?"))
        return pb.VCBCReply()  # fill fields if your proto expects something specific

    def abba(self, request: pb.ABBARequest, variant: str) -> pb.ABBAReply:
        logging.info("[%s] ABBA from=%s inst=%s", variant, getattr(request, "id", "?"), getattr(request, "instance", "?"))
        return pb.ABBAReply()

    def propose(self, request: pb.PRORequest) -> pb.PROReply:
        logging.info("[pmvba] Propose from=%s view=%s", getattr(request, "id", "?"), getattr(request, "view", "?"))
        return pb.PROReply()

    def classic_propose(self, request: pb.ClassicPRORequest) -> pb.ClassicPROReply:
        logging.info("[cachin_mvba] ClassicPropose from=%s view=%s", getattr(request, "id", "?"), getattr(request, "view", "?"))
        return pb.ClassicPROReply()

    def classic_commit(self, request: pb.ClassicCommitRequest) -> pb.ClassicCommitReply:
        logging.info("[cachin_mvba] ClassicCommit from=%s view=%s", getattr(request, "id", "?"), getattr(request, "view", "?"))
        return pb.ClassicCommitReply()

    def collect_proposal(self, request: pb.CPRORequest) -> pb.CPROReply:
        logging.info("[collector] CollectProposal from=%s view=%s", getattr(request, "id", "?"), getattr(request, "view", "?"))
        return pb.CPROReply()

    def recommend(self, request: pb.RECORequest) -> pb.RECOReply:
        logging.info("[pmvba] Recommend from=%s view=%s", getattr(request, "id", "?"), getattr(request, "view", "?"))
        return pb.RECOReply()

    def elect_leader(self, request: pb.ELeaderRequest) -> pb.ELeaderReply:
        logging.info("[leader] ElectLeader from=%s view=%s", getattr(request, "id", "?"), getattr(request, "view", "?"))
        return pb.ELeaderReply()

    # Optional: keep SayHello for legacy/tests
    def say_hello(self, request: pb.HelloRequest) -> pb.HelloReply:
        logging.info("[hello] from name=%s", request.name)
        return pb.HelloReply(message=f"ack from node {self.node_id}")


# --------------------------------
# gRPC Servicer implementation
# --------------------------------
class NodeServicer(pb_grpc.GreeterServicer):
    def __init__(self, node_id: int, handlers: ProtocolHandlers):
        self.node_id = node_id
        self.h = handlers

    # --- legacy/demo ---
    def SayHello(self, request, context):
        return self.h.say_hello(request)

    # --- your real RPCs ---
    def VCBC(self, request, context):
        return self.h.vcbc(request, variant="vcbc")

    def ClassicVCBC(self, request, context):
        return self.h.vcbc(request, variant="classic_vcbc")

    def pVCBC(self, request, context):
        return self.h.vcbc(request, variant="pvcbc")

    def ABBA(self, request, context):
        return self.h.abba(request, variant="abba")

    def ClassicABBA(self, request, context):
        return self.h.abba(request, variant="classic_abba")

    def Propose(self, request, context):
        try:
          self.pmvba.on_propose(request)
          return pb.PROReply()
        except Exception as e:
          logging.error("Propose failed: %s", e)
          context.set_code(grpc.StatusCode.INTERNAL)
          context.set_details(str(e))
          return pb.PROReply()
        
        #return self.h.propose(request)

    def ClassicPropose(self, request, context):
        return self.h.classic_propose(request)

    def ClassicCommit(self, request, context):
        return self.h.classic_commit(request)

    def CollectProposal(self, request, context):
        return self.h.collect_proposal(request)

    def Recommend(self, request, context):
        try:
           self.pmvba.on_reco(request)
           return pb.RECOReply()
        except Exception as e:
          logging.exception("Recommend handler failed")
          context.set_code(grpc.StatusCode.INTERNAL)
          context.set_details(str(e))
          return pb.RECOReply()
        #return self.h.recommend(request)

    def ElectLeader(self, request, context):
        return self.h.elect_leader(request)

    # Streaming methods exist in the proto; keep them unimplemented unless you use them
    def SayHelloStreamReply(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Not used in this framework")
        return pb.HelloReply()

    def SayHelloBidiStream(self, request_iterator, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Not used in this framework")
        yield pb.HelloReply()


def serve(node_id: int, host: str, port: int, max_workers: int = 32) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    handlers = ProtocolHandlers(node_id=node_id)
    pb_grpc.add_GreeterServicer_to_server(NodeServicer(node_id=node_id, handlers=handlers), server)

    bind_addr = f"{host}:{port}"
    server.add_insecure_port(bind_addr)
    server.start()
    logging.info("Node %d listening on %s", node_id, bind_addr)
    server.wait_for_termination()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--node_id", type=int, required=True)
    ap.add_argument("--host", type=str, default="0.0.0.0")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--workers", type=int, default=32)
    args = ap.parse_args()

    serve(node_id=args.node_id, host=args.host, port=args.port, max_workers=args.workers)


if __name__ == "__main__":
    main()
