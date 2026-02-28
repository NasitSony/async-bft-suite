# src/bitvec.py
from proto import helloworld_pb2
from config import constants as Constants
from . import transport

def bitvec_to_str(bits):
    return "".join("1" if b else "0" for b in bits)

def str_to_bitvec(s: str, n: int):
    s = (s or "").strip()
    if len(s) != n or any(c not in "01" for c in s):
        return None
    return [1 if c == "1" else 0 for c in s]

def on_certproposal_maybe_broadcast_bitvec(ctx, inst: int):
    """
    When ctx.certified_props[inst] reaches quorum (>=q),
    build own bitvector over proposers and broadcast BITVEC once.
    """
    props = ctx.certified_props.get(inst, {})
    cnt = len(props)
    if cnt < ctx.q:
        return

    if inst in ctx.bitvec_sent:
        return
    ctx.bitvec_sent.add(inst)

    bits = [0] * ctx.n
    for proposer in props.keys():
        idx = ctx.id_to_index.get(proposer)
        if idx is not None:
            bits[idx] = 1

    bitstr = bitvec_to_str(bits)
    print(f"[{ctx.node_id}] 📦 bitvec(inst={inst})={bitstr}", flush=True)
    print(f"[{ctx.node_id}] 📣 broadcasting BITVEC inst={inst} bits={bitstr} (certprops={cnt} q={ctx.q})", flush=True)

    # store own bitvec locally too
    ctx.bitvecs.setdefault(inst, {})[ctx.node_id] = bits

    # broadcast to peers via Propose(type="BITVEC")
    req = helloworld_pb2.PRORequest(
        id=ctx.node_id,
        type="BITVEC",
        instance=inst,
        proof="",
        value=bitstr,
    )
    for port in Constants.PORTLIST[: ctx.n]:
        if port == ctx.port:
            continue
        try:
            transport.get_stub(ctx, port).Propose(req, timeout=2.0)
        except Exception as e:
            print(f"[{ctx.node_id}] BITVEC send failed to {port}: {e}", flush=True)

def maybe_aggregate_support(ctx, inst: int):
    """
    If we have >=q BITVECs, aggregate support S[j]=OR over received vectors.
    Store once at ctx.support_set[inst].
    """
    bv_map = ctx.bitvecs.get(inst, {})
    got = len(bv_map)
    if got < ctx.q:
        return None
    if inst in ctx.support_set:
        return ctx.support_set[inst]

    agg = [0] * ctx.n
    for bits in bv_map.values():
        for j in range(ctx.n):
            if bits[j] == 1:
                agg[j] = 1

    ctx.support_set[inst] = agg
    return agg

def on_bitvec(ctx, sender: str, inst: int, bitstr: str, abba_start_cb=None):
    bits = str_to_bitvec(bitstr, ctx.n)
    if bits is None:
        print(f"[{ctx.node_id}] ⚠️ invalid BITVEC from={sender} inst={inst} value={bitstr!r}", flush=True)
        return

    ctx.bitvecs.setdefault(inst, {})[sender] = bits
    got = len(ctx.bitvecs[inst])
    print(f"[{ctx.node_id}] ✅ received BITVEC inst={inst} from={sender} bits={bitstr} (got={got}/{ctx.q})", flush=True)

    if inst in ctx.support_ready:
        return

    S = maybe_aggregate_support(ctx, inst)
    if S is None:
        return

    ctx.support_ready.add(inst)
    Sstr = bitvec_to_str(S)
    print(f"[{ctx.node_id}] ✅ SUPPORT ready inst={inst} S={Sstr} (from {got} BITVECs)", flush=True)
    
    if abba_start_cb is not None:
        abba_start_cb(inst, S)