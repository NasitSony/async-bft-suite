# src/abba.py
from proto import helloworld_pb2
from config import constants as Constants
from . import coin

ABSTAIN = -1

def _store(ctx, inst, rnd, mtype, sender, bit):
    inst_map = ctx.abba_messages.setdefault(inst, {})
    rnd_map = inst_map.setdefault(rnd, {})
    typ_map = rnd_map.setdefault(mtype, {})
    if sender in typ_map:
        return False
    typ_map[sender] = bit
    return True

def _count(ctx, inst, rnd, mtype, bit=None):
    typ_map = ctx.abba_messages.get(inst, {}).get(rnd, {}).get(mtype, {})
    if bit is None:
        return len(typ_map)
    return sum(1 for b in typ_map.values() if b == bit)

def _values(ctx, inst, rnd, mtype):
    return list(ctx.abba_messages.get(inst, {}).get(rnd, {}).get(mtype, {}).values())

def _has(ctx, inst, rnd, mtype, bit):
    return any(b == bit for b in _values(ctx, inst, rnd, mtype))

def broadcast_abba(ctx, get_stub, inst, rnd, bit, mtype, justification=""):
    msg = helloworld_pb2.messageABBA(
        instance=int(inst),
        round=int(rnd),
        value=int(bit),
        justification=justification,
        sign="",
        type=mtype,
        id=ctx.node_id,
    )
    req = helloworld_pb2.ABBARequest(message=msg)

    for port in Constants.PORTLIST[: ctx.n]:
        if port == ctx.port:
            continue
        try:
            get_stub(port).ABBA(req, timeout=2.0)
        except Exception as e:
            print(f"[{ctx.node_id}] ABBA send failed to {port}: {e}", flush=True)

def start(ctx, inst, input_bit=None, justification="", get_stub=None, bit=None):
    # accept alias bit
    if input_bit is None:
        input_bit = bit
    if input_bit is None:
        raise ValueError("ABBA start requires input_bit (or bit alias)")
    if get_stub is None:
        raise ValueError("ABBA start requires get_stub callable(port)->stub")

    input_bit = int(input_bit)

    if inst in ctx.abba_started or inst in ctx.abba_decided:
        return
    ctx.abba_started.add(inst)

    print(f"[{ctx.node_id}] 🚀 ABBA start inst={inst} input_bit={input_bit}", flush=True)
    # Round 1 PREPROCESS
    broadcast_abba(ctx, get_stub, inst, 1, input_bit, Constants.PREPROCESS, justification=justification)

def _maybe_send_prevote_r_gt_1(ctx, get_stub, inst, rnd):
    """
    For rnd>1: derive PREVOTE(rnd) from MAINVOTE(rnd-1) (or coin if all abstain).
    """
    if rnd <= 1:
        return

    sent_key = (inst, rnd, Constants.PREVOTE)
    if sent_key in ctx.abba_sent:
        return

    prev_r = rnd - 1
    if _count(ctx, inst, prev_r, Constants.MAINVOTE) < ctx.q:
        return

    # If any mainvote 0 exists => b=0; else if any 1 exists => b=1; else coin(prev_r)
    if _has(ctx, inst, prev_r, Constants.MAINVOTE, 0):
        b = 0
    elif _has(ctx, inst, prev_r, Constants.MAINVOTE, 1):
        b = 1
    else:
        # all abstain -> must have coin(prev_r) ready
        cb = ctx.coins.get((inst, prev_r))
        if cb is None:
            return
        b = int(cb)

    ctx.abba_sent.add(sent_key)
    print(f"[{ctx.node_id}] ✅ PREVOTE r={rnd} derived from MAINVOTE r={prev_r} -> b={b}", flush=True)
    broadcast_abba(ctx, get_stub, inst, rnd, b, Constants.PREVOTE)

def on_abba_message(ctx, get_stub, inst: int, rnd: int, mtype: str, sender: str, bit: int, justification: str = ""):
    if inst in ctx.abba_decided:
        return

    # ---- COIN messages carry a share (0/1). Store & combine at q.
    if mtype == Constants.COIN:
        share = int(bit) & 1
        coin_bit = coin.on_coin_share(ctx, inst, rnd, sender, share)
        if coin_bit is not None:
            ctx.coins[(inst, rnd)] = int(coin_bit)
            # coin of round rnd is used only if previous round mainvotes were all abstain,
            # but we can now *try* to derive PREVOTE(rnd+1).
            _maybe_send_prevote_r_gt_1(ctx, get_stub, inst, rnd + 1)
        return

    bit = int(bit)

    # ---- store/dedup
    if not _store(ctx, inst, rnd, mtype, sender, bit):
        return

    print(f"[{ctx.node_id}] 📨 ABBA | inst={inst} | r={rnd} | type={mtype} | from={sender} | bit={bit} | just={justification}", flush=True)

    # ---- PREPROCESS -> PREVOTE (ONLY round 1)
    if mtype == Constants.PREPROCESS and rnd == 1:
        if _count(ctx, inst, rnd, Constants.PREPROCESS) >= ctx.q:
            c1 = _count(ctx, inst, rnd, Constants.PREPROCESS, 1)
            c0 = _count(ctx, inst, rnd, Constants.PREPROCESS, 0)
            b = 1 if c1 >= c0 else 0
            key = (inst, rnd, Constants.PREVOTE)
            if key not in ctx.abba_sent:
                ctx.abba_sent.add(key)
                print(f"[{ctx.node_id}] ✅ PREPROCESS quorum inst={inst} r=1 -> PREVOTE {b}", flush=True)
                broadcast_abba(ctx, get_stub, inst, rnd, b, Constants.PREVOTE)

    # ---- PREVOTE -> MAINVOTE (0/1/ABSTAIN)
    if mtype == Constants.PREVOTE:
        if _count(ctx, inst, rnd, Constants.PREVOTE) >= ctx.q:
            c1 = _count(ctx, inst, rnd, Constants.PREVOTE, 1)
            c0 = _count(ctx, inst, rnd, Constants.PREVOTE, 0)

            if c1 >= ctx.q:
                mv = 1
            elif c0 >= ctx.q:
                mv = 0
            else:
                mv = ABSTAIN

            key = (inst, rnd, Constants.MAINVOTE)
            if key not in ctx.abba_sent:
                ctx.abba_sent.add(key)
                print(f"[{ctx.node_id}] ✅ PREVOTE quorum inst={inst} r={rnd} -> MAINVOTE {mv}", flush=True)
                broadcast_abba(ctx, get_stub, inst, rnd, mv, Constants.MAINVOTE)

    # ---- MAINVOTE: decide OR start coin(rnd)
    if mtype == Constants.MAINVOTE:
        if _count(ctx, inst, rnd, Constants.MAINVOTE) >= ctx.q:
            # Decide only if q mainvotes and ALL are 0 OR ALL are 1
            vals = _values(ctx, inst, rnd, Constants.MAINVOTE)
            # (vals length may exceed q; still fine)
            if vals and all(v == 1 for v in vals):
                decided = 1
            elif vals and all(v == 0 for v in vals):
                decided = 0
            else:
                decided = None

            if decided is not None:
                if inst not in ctx.abba_decided:
                    ctx.abba_decided[inst] = decided
                    print(f"[{ctx.node_id}] 🏁 ABBA DECIDE inst={inst} bit={decided} (r={rnd})", flush=True)
                    broadcast_abba(ctx, get_stub, inst, rnd, decided, Constants.DECISION)
                return

            # No decision => broadcast my coin share once for this round
            if (inst, rnd) not in ctx.coin_sent:
                ctx.coin_sent.add((inst, rnd))
                my_share = coin.make_share(ctx.node_id, inst, rnd)
                print(f"[{ctx.node_id}] 🪙 no-decision => broadcast COIN SHARE inst={inst} r={rnd} share={my_share}", flush=True)
                broadcast_abba(ctx, get_stub, inst, rnd, my_share, Constants.COIN)

                # also feed my own share locally (so I can reach q without waiting on myself via RPC)
                coin_bit = coin.on_coin_share(ctx, inst, rnd, ctx.node_id, my_share)
                if coin_bit is not None:
                    ctx.coins[(inst, rnd)] = int(coin_bit)
                    _maybe_send_prevote_r_gt_1(ctx, get_stub, inst, rnd + 1)

            # Regardless, try to derive PREVOTE(rnd+1) from MAINVOTE(rnd) if possible
            _maybe_send_prevote_r_gt_1(ctx, get_stub, inst, rnd + 1)

    # ---- DECISION receive (optional)
    if mtype == Constants.DECISION:
        if inst not in ctx.abba_decided:
            ctx.abba_decided[inst] = int(bit)
            print(f"[{ctx.node_id}] ✅ ABBA DECISION learned inst={inst} bit={bit} (r={rnd})", flush=True)