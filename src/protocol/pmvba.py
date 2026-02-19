from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set, Optional, List, Callable
import time
import logging

import helloworld_pb2 as pb


# ----------------------------
# Per-instance protocol state
# ----------------------------
@dataclass
class PmvbaState:
    instance: int
    proposed_value: Optional[str] = None

    # recommendation votes: value -> set(sender_ids)
    reco_votes: Dict[str, Set[str]] = field(default_factory=dict)

    decided: bool = False
    decided_value: Optional[str] = None

    t0: float = field(default_factory=time.time)


# ----------------------------
# PMVBA Protocol "brain"
# ----------------------------
class PMVBAProtocol:
    """
    PMVBA prototype (no crypto), built on your existing proto messages:

    PRORequest:
      id (string), type (string), instance (int), proof (string), value (string)

    RECORequest:
      id (string), type (string), instance (int), recomID (string), proof (string), value (string)

    Network rule:
    - gRPC reply is only ACK/empty reply.
    - Any follow-up protocol steps are sent as NEW messages via NodeClient.
    """

    def __init__(
        self,
        node_id: str,
        peers: List[str],
        f: int,
        send_propose: Callable[[str, pb.PRORequest], None],
        send_reco: Callable[[str, pb.RECORequest], None],
        logger: Optional[logging.Logger] = None,
    ):
        """
        node_id: string (because proto 'id' is string)
        peers: list of peer ids (strings). Include self or not—either is OK but be consistent.
        f: byzantine fault threshold
        send_propose(peer_id, req): transport hook that sends PRORequest to peer
        send_reco(peer_id, req): transport hook that sends RECORequest to peer
        """
        self.node_id = node_id
        self.peers = peers
        self.f = f
        self.q_2f1 = 2 * f + 1

        self.send_propose = send_propose
        self.send_reco = send_reco

        self.states: Dict[int, PmvbaState] = {}
        self.log = logger or logging.getLogger("pmvba")

    # -------------
    # state helpers
    # -------------
    def _st(self, instance: int) -> PmvbaState:
        if instance not in self.states:
            self.states[instance] = PmvbaState(instance=instance)
        return self.states[instance]

    # ----------------------------
    # Public: start local proposal
    # ----------------------------
    def start(self, instance: int, value: str) -> None:
        """
        Called by your driver/coordinator when THIS node wants to propose.
        """
        st = self._st(instance)
        if st.decided:
            return

        st.proposed_value = value
        self.broadcast_propose(instance=instance, value=value)

    # ----------------------------
    # Incoming handlers (called by server)
    # ----------------------------
    def on_propose(self, req: pb.PRORequest) -> pb.PROReply:
        """
        Handle incoming PRORequest.
        """
        sender = req.id
        instance = req.instance
        msg_type = (req.type or "PROPOSE").upper()
        value = req.value or ""

        st = self._st(instance)
        if st.decided:
            return pb.PROReply()

        if not sender or not value:
            return pb.PROReply()

        # Accept proposal (simple rule: first wins). Replace with your pMVBA logic.
        if st.proposed_value is None:
            st.proposed_value = value
            self.log.info("[pmvba] inst=%d accepted proposal value=%s from=%s",
                          instance, value[:64], sender)

            # After receiving a proposal, cast a RECO vote for it (prototype behavior).
            # In your real pMVBA, this might be gated by VCBC/committee steps.
            self.broadcast_reco(instance=instance, value=value, recom_id="")

        return pb.PROReply()

    def on_reco(self, req: pb.RECORequest) -> pb.RECOReply:
        """
        Handle incoming RECORequest.
        """
        sender = req.id
        instance = req.instance
        msg_type = (req.type or "RECO").upper()
        value = req.value or ""

        st = self._st(instance)
        if st.decided:
            return pb.RECOReply()

        if not sender or not value:
            return pb.RECOReply()

        # If someone announces DECIDE, accept it (prototype).
        if msg_type == "DECIDE":
            self._decide(st, value, reason=f"DECIDE from {sender}")
            return pb.RECOReply()

        # Otherwise treat as RECO vote.
        voters = st.reco_votes.setdefault(value, set())
        if sender in voters:
            return pb.RECOReply()
        voters.add(sender)

        # Decide condition (prototype):
        # If 2f+1 votes for same value, decide.
        if not st.decided and len(voters) >= self.q_2f1:
            self._decide(st, value, reason=f"reco quorum {len(voters)}>=2f+1")
            self.broadcast_decide(instance=instance, value=value)

        return pb.RECOReply()

    # ----------------------------
    # Outbound helpers (use client)
    # ----------------------------
    def broadcast_propose(self, instance: int, value: str) -> None:
        req = pb.PRORequest(
            id=self.node_id,
            type="PROPOSE",
            instance=instance,
            proof="",   # no crypto
            value=value,
        )
        for p in self.peers:
            self.send_propose(p, req)

    def broadcast_reco(self, instance: int, value: str, recom_id: str = "") -> None:
        req = pb.RECORequest(
            id=self.node_id,
            type="RECO",
            instance=instance,
            recomID=recom_id,
            proof="",   # no crypto
            value=value,
        )
        for p in self.peers:
            self.send_reco(p, req)

    def broadcast_decide(self, instance: int, value: str) -> None:
        req = pb.RECORequest(
            id=self.node_id,
            type="DECIDE",
            instance=instance,
            recomID="",
            proof="",
            value=value,
        )
        for p in self.peers:
            self.send_reco(p, req)

    # ----------------------------
    # internal
    # ----------------------------
    def _decide(self, st: PmvbaState, value: str, reason: str) -> None:
        if st.decided:
            return
        st.decided = True
        st.decided_value = value
        dt = time.time() - st.t0
        self.log.info("[pmvba] ✅ DECIDE inst=%d value=%s latency=%.3fs (%s)",
                      st.instance, value[:64], dt, reason)
