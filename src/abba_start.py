# src/abba_start.py
from config import constants as Constants
from . import abba  # add this import at top
from . import transport

def compute_permutation(ctx, inst: int):
    """
    Deterministic 'common permutation' without coin (for now):
    rotate the id list by inst (or hash(inst)).
    Everyone can compute the same order.
    """
    ids = [f"id{i}" for i in range(1, ctx.n + 1)]
    k = inst % ctx.n
    return ids[k:] + ids[:k]



def start_abba_if_ready(ctx, inst: int, S_bits, get_stub):
    #if inst in ctx.abba_started:
       # return
    #ctx.abba_started.add(inst)
    if inst in ctx.abba_started or inst in ctx.abba_decided:
        return


    perm = compute_permutation(ctx, inst)
    pivot = perm[0]
    idx = ctx.id_to_index[pivot]
    b = 1 if S_bits[idx] == 1 else 0

    print(f"[{ctx.node_id}] 🚀 ABBA START inst={inst} perm={perm} pivot={pivot} input_bit={b}", flush=True)

    get_stub = lambda port: transport.get_stub(ctx, port)
    # ✅ REAL SEND (this replaces the stub)

    abba.start(
        ctx=ctx, 
        inst=inst, 
        input_bit=b, 
        get_stub=get_stub, 
        justification=f"pivot={pivot}"
    )

    print(f"[{ctx.node_id}] 📣 ABBA PREPROCESS broadcast inst={inst} bit={b}", flush=True)

