# src/mvba.py
import hashlib, random
from config import constants as Constants
from . import abba
from . import transport

def common_perm(ctx, inst: int):
    # shared deterministic permutation
    node_ids = list(ctx.node_ids)
    seed_material = f"{getattr(Constants,'PERM_SALT','perm')}|inst={inst}|nodes={','.join(node_ids)}"
    digest = hashlib.sha256(seed_material.encode()).digest()
    seed = int.from_bytes(digest[:8], "big")
    rng = random.Random(seed)
    rng.shuffle(node_ids)
    return node_ids

def _pivot_bit(ctx, inst: int, perm):
    S = ctx.support_set.get(inst)
    if S is None:
        return None, None
    pivot = perm[0]
    idx = ctx.id_to_index.get(pivot)
    if idx is None:
        return None, None
    return int(S[idx]), pivot

def try_start_mvba(ctx, inst: int, get_stub):
    if inst in ctx.mvba_started:
        return
    if inst not in ctx.support_ready:
        return

    perm = common_perm(ctx, inst)
    bit, pivot = _pivot_bit(ctx, inst, perm)
    if bit is None:
        print(f"[{ctx.node_id}] ⚠️ MVBA start blocked inst={inst}: missing S/pivot mapping", flush=True)
        return

    ctx.mvba_started.add(inst)
    ctx.mvba_perm[inst] = perm
    ctx.mvba_pivot[inst] = pivot

    get_stub = lambda port: transport.get_stub(ctx, port)

    print(f"[{ctx.node_id}] 🚀 MVBA->ABA START inst={inst} perm={perm} pivot={pivot} input_bit={bit}", flush=True)
    abba.start(ctx, inst=inst, input_bit=bit, get_stub=get_stub, justification=f"pivot={pivot}")

def _select_proposer(ctx, inst: int, decided_bit: int):
    perm = ctx.mvba_perm.get(inst)
    S = ctx.support_set.get(inst)
    if perm is None or S is None:
        return None

    for pid in perm:
        idx = ctx.id_to_index.get(pid)
        if idx is None:
            continue
        if int(S[idx]) == int(decided_bit):
            return pid
    return None

def on_aba_decide(ctx, inst: int, decided_bit: int):
    proposer = _select_proposer(ctx, inst, decided_bit)
    if proposer is None:
        print(f"[{ctx.node_id}] ⚠️ MVBA finalize failed inst={inst}: no proposer matches bit={decided_bit}", flush=True)
        return

    chosen = ctx.certified_props.get(inst, {}).get(proposer)
    print(f"[{ctx.node_id}] ✅ MVBA SELECT inst={inst} bit={decided_bit} proposer={proposer}", flush=True)

    if chosen is None:
        print(f"[{ctx.node_id}] ⚠️ MVBA missing CERTPROPOSAL for proposer={proposer} inst={inst}", flush=True)
        return

    ctx.mvba_decided[inst] = {"proposer": proposer, "value": chosen["value"], "proof": chosen["proof"]}
    print(f"[{ctx.node_id}] 🏁 MVBA DECIDE inst={inst} value={chosen['value']} proposer={proposer}", flush=True)