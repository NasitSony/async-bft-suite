# src/context.py
from dataclasses import dataclass, field
import threading
from config import constants as Constants

@dataclass
class NodeContext:
    node_id: str
    port: int

    # cluster config
    n: int = field(default_factory=lambda: getattr(Constants, "N", len(Constants.PORTLIST)))
    f: int = 0
    q: int = 0  # quorum = 2f+1

    # stub cache
    stubs: dict = field(default_factory=dict)
    stub_lock: threading.Lock = field(default_factory=threading.Lock)

    # protocol state
    proposeMessage: dict = field(default_factory=dict)      # "instance<k>" -> {value,...}
    certs: dict = field(default_factory=dict)               # (inst,tag,step,value)->set(sender_ids)
    my_cert_sent: set = field(default_factory=set)          # inst set
    certified_props: dict = field(default_factory=dict)     # inst -> proposer -> {"value","proof"}

    # BITVEC / SUPPORT / ABBA hooks
    id_to_index: dict = field(default_factory=dict)       # "id1"->0, ...
    certprop_counted: set = field(default_factory=set)    # (inst, proposer) dedup

    bitvec_sent: set = field(default_factory=set)         # inst
    bitvecs: dict = field(default_factory=dict)           # inst -> sender -> [0/1]*n
    support_set: dict = field(default_factory=dict)       # inst -> [0/1]*n
    support_ready: set = field(default_factory=set)       # inst

    abba_started: set = field(default_factory=set)        # inst

    abba_messages: dict = field(default_factory=dict)
    abba_sent: set = field(default_factory=set)
    abba_decided: dict = field(default_factory=dict) # inst -> decided bit

    # MVBA fields
    node_ids: list = field(default_factory=list)            # ['id1','id2',...]
    mvba_started: set = field(default_factory=set)          # inst.mvba_perm: dict = field(default_factory=dict)           # inst -> [ids]
    mvba_pivot: dict = field(default_factory=dict)          # inst -> pivot id
    mvba_decided: dict = field(default_factory=dict)        # inst -> {proposer,value,proof}
    mvba_on_aba_decide: object = None                       # callable(inst, decided_bit)

    abba_round: dict = field(default_factory=dict)      # inst -> current round (int)
    abba_est: dict = field(default_factory=dict)        # inst -> current estimate bit
    abba_coin: dict = field(default_factory=dict)       # (inst, round) -> coin bit
    abba_sent: set = field(default_factory=set)         # (inst, round, type) dedup sends

    # coin (simulated)
    coin_shares: dict = field(default_factory=dict)   # inst -> rnd -> sender -> 0/1
    coin_ready: set = field(default_factory=set)      # (inst, rnd)
    coin_sent: set = field(default_factory=set)       # (inst, rnd)
    coins: dict = field(default_factory=dict)         # (inst, rnd) -> coin bit 0/1 (cached)

    def init_quorum(self):
        # derive f safely from n (BFT expects n >= 3f+1)
        self.f = min(getattr(Constants, "FAULTY_NODES", 1), (self.n - 1) // 3)
        self.q = 2 * self.f + 1

        # deterministic id order: id1..idN mapped to indices 0..n-1
        ids = [f"id{i}" for i in range(1, self.n + 1)]
        self.node_ids = ids
        self.id_to_index = {pid: i for i, pid in enumerate(ids)}