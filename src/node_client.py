# greeter_client.py
"""
Common gRPC node client for your async-BFT protocol suite.

- Each node uses ONE client object to talk to other nodes' servers.
- Provides typed wrappers for your existing RPCs (VCBC/ABBA/Propose/etc).
- Replies are just the RPC reply messages; protocol progress should happen via new outbound RPCs.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import grpc

import helloworld_pb2 as pb
import helloworld_pb2_grpc as pb_grpc

Peer = Tuple[int, str]  # (peer_id, "host:port")


def parse_peers(raw: str) -> List[Peer]:
    """
    raw format: "1=127.0.0.1:50051,2=127.0.0.1:50052"
    """
    peers: List[Peer] = []
    if not raw.strip():
        return peers
    for part in raw.split(","):
        pid_s, addr = part.split("=")
        peers.append((int(pid_s), addr))
    return peers


@dataclass
class NodeClient:
    peers: List[Peer]
    _channels: Dict[int, grpc.Channel] = None
    _stubs: Dict[int, pb_grpc.GreeterStub] = None

    def __post_init__(self) -> None:
        self._channels = {}
        self._stubs = {}

    def _addr(self, peer_id: int) -> str:
        m = dict(self.peers)
        if peer_id not in m:
            raise ValueError(f"Unknown peer_id={peer_id}")
        return m[peer_id]

    def stub(self, peer_id: int) -> pb_grpc.GreeterStub:
        if peer_id in self._stubs:
            return self._stubs[peer_id]
        ch = grpc.insecure_channel(self._addr(peer_id))
        st = pb_grpc.GreeterStub(ch)
        self._channels[peer_id] = ch
        self._stubs[peer_id] = st
        return st

    # --------------------
    # Typed RPC wrappers
    # --------------------
    def vcbc(self, peer_id: int, req: pb.VCBCRequest, timeout_s: float = 3.0) -> pb.VCBCReply:
        return self.stub(peer_id).VCBC(req, timeout=timeout_s)

    def classic_vcbc(self, peer_id: int, req: pb.VCBCRequest, timeout_s: float = 3.0) -> pb.VCBCReply:
        return self.stub(peer_id).ClassicVCBC(req, timeout=timeout_s)

    def pvcbc(self, peer_id: int, req: pb.VCBCRequest, timeout_s: float = 3.0) -> pb.VCBCReply:
        return self.stub(peer_id).pVCBC(req, timeout=timeout_s)

    def abba(self, peer_id: int, req: pb.ABBARequest, timeout_s: float = 3.0) -> pb.ABBAReply:
        return self.stub(peer_id).ABBA(req, timeout=timeout_s)

    def classic_abba(self, peer_id: int, req: pb.ABBARequest, timeout_s: float = 3.0) -> pb.ABBAReply:
        return self.stub(peer_id).ClassicABBA(req, timeout=timeout_s)

    def propose(self, peer_id: int, req: pb.PRORequest, timeout_s: float = 3.0) -> pb.PROReply:
        return self.stub(peer_id).Propose(req, timeout=timeout_s)

    def classic_propose(self, peer_id: int, req: pb.ClassicPRORequest, timeout_s: float = 3.0) -> pb.ClassicPROReply:
        return self.stub(peer_id).ClassicPropose(req, timeout=timeout_s)

    def classic_commit(self, peer_id: int, req: pb.ClassicCommitRequest, timeout_s: float = 3.0) -> pb.ClassicCommitReply:
        return self.stub(peer_id).ClassicCommit(req, timeout=timeout_s)

    def collect_proposal(self, peer_id: int, req: pb.CPRORequest, timeout_s: float = 3.0) -> pb.CPROReply:
        return self.stub(peer_id).CollectProposal(req, timeout=timeout_s)

    def recommend(self, peer_id: int, req: pb.RECORequest, timeout_s: float = 3.0) -> pb.RECOReply:
        return self.stub(peer_id).Recommend(req, timeout=timeout_s)

    def elect_leader(self, peer_id: int, req: pb.ELeaderRequest, timeout_s: float = 3.0) -> pb.ELeaderReply:
        return self.stub(peer_id).ElectLeader(req, timeout=timeout_s)

    def close(self) -> None:
        for ch in self._channels.values():
            ch.close()


# --------------------
# small demo (optional)
# --------------------
def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    ap = argparse.ArgumentParser()
    ap.add_argument("--peers", type=str, required=True)
    ap.add_argument("--to", type=int, required=True)
    ap.add_argument("--sender_id", type=str, default="client")
    ap.add_argument("--view", type=int, default=1)
    args = ap.parse_args()

    peers = parse_peers(args.peers)
    c = NodeClient(peers=peers)

    # Minimal safe demo: SayHello still exists
    rep = c.stub(args.to).SayHello(pb.HelloRequest(name=f"from {args.sender_id}"))
    logging.info("SayHello reply: %s", rep.message)

    c.close()


if __name__ == "__main__":
    main()
