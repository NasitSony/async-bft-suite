# src/coin.py
import hashlib

def make_share(node_id: str, inst: int, rnd: int) -> int:
    s = f"{node_id}|{inst}|{rnd}".encode()
    h = hashlib.sha256(s).digest()
    return h[0] & 1

def combine(shares: list[int]) -> int:
    x = 0
    for b in shares:
        x ^= (int(b) & 1)
    return x

def on_coin_share(ctx, inst: int, rnd: int, sender: str, share_bit: int):
    inst_map = ctx.coin_shares.setdefault(inst, {})
    rnd_map = inst_map.setdefault(rnd, {})

    if sender in rnd_map:
        return None

    rnd_map[sender] = int(share_bit) & 1
    got = len(rnd_map)
    print(f"[{ctx.node_id}] 🪙 COIN share recv inst={inst} r={rnd} from={sender} share={share_bit} (got={got}/{ctx.q})", flush=True)

    if got >= ctx.q and (inst, rnd) not in ctx.coin_ready:
        ctx.coin_ready.add((inst, rnd))
        coin_bit = combine(list(rnd_map.values()))
        print(f"[{ctx.node_id}] 🪙 COIN READY inst={inst} r={rnd} coin={coin_bit}", flush=True)
        return coin_bit

    return None