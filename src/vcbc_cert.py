# src/vcbc_cert.py
from config import constants as Constants
from . import transport
from . import bitvec  # add at top or inside

def _cert_add(ctx, inst: int, tag: str, step: int, value: str, sender: str) -> bool:
    key = (inst, tag, step, value)
    s = ctx.certs.setdefault(key, set())
    before = len(s)
    s.add(sender)
    after = len(s)
    # fire once at crossing quorum
    return before < ctx.q and after >= ctx.q

def try_broadcast_my_cert_if_ready(ctx, inst: int, step: int, value: str):
    # need local input first
    pkey = Constants.INSTANCE + str(inst)
    if pkey not in ctx.proposeMessage:
        return

    my_value = ctx.proposeMessage[pkey][Constants.VALUE]
    if my_value != value:
        return

    if inst in ctx.my_cert_sent:
        return

    cert_key = (inst, "VCBC", step, value)
    signers = ctx.certs.get(cert_key, set())
    if len(signers) < ctx.q:
        return

    ctx.my_cert_sent.add(inst)
    proof = f"QC|proposer={ctx.node_id}|inst={inst}|step={step}|signers=" + ",".join(sorted(signers))

    ctx.certified_props.setdefault(inst, {})[ctx.node_id] = {"value": value, "proof": proof}

    print(f"[{ctx.node_id}] 📣 (late/now) broadcasting CERTPROPOSAL inst={inst} proposer={ctx.node_id} value={value}", flush=True)
    transport.broadcast_certproposal(ctx, inst=inst, proposer=ctx.node_id, value=value, proof=proof)

def on_vcbc(ctx, sender: str, msg):
    inst = msg.instance
    step = msg.step
    value = msg.value

    crossed = _cert_add(ctx, inst, "VCBC", step, value, sender)
    if not crossed:
        return

    print(f"[{ctx.node_id}] ✅ VCBC cert ready inst={inst} step={step} value={value} (q={ctx.q})", flush=True)
    # whether or not we already have local input, try now
    try_broadcast_my_cert_if_ready(ctx, inst, step, value)

def on_certproposal(ctx, proposer: str, inst: int, value: str, proof: str):
    props = ctx.certified_props.setdefault(inst, {})
    if proposer not in props:
        props[proposer] = {"value": value, "proof": proof}
    cnt = len(props)
    print(f"[{ctx.node_id}] ✅ received CERTPROPOSAL inst={inst} proposer={proposer} value={value} (count={cnt})", flush=True)
    bitvec.on_certproposal_maybe_broadcast_bitvec(ctx, inst)