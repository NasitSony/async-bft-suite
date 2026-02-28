# src/transport.py
import grpc
from proto import helloworld_pb2
from proto import helloworld_pb2_grpc
from config import constants as Constants

def get_stub(ctx, port: int):
    with ctx.stub_lock:
        if port not in ctx.stubs:
            ch = grpc.insecure_channel(f"localhost:{port}")
            ctx.stubs[port] = helloworld_pb2_grpc.GreeterStub(ch)
        return ctx.stubs[port]

def broadcast_vcbc(ctx, inst: int, step: int, value: str, timeout_s: float = 2.0):
    msg = helloworld_pb2.mDict(instance=inst, step=step, ts="1", value=value, id=ctx.node_id)
    req = helloworld_pb2.VCBCRequest(msg=msg)

    for port in Constants.PORTLIST[: ctx.n]:
        if port == ctx.port:
            continue
        try:
            reply = get_stub(ctx, port).VCBC(req, timeout=timeout_s)
            if reply and reply.msg:
                print(f"[{ctx.node_id}] 📨 VCBC reply from {reply.msg.id} inst={reply.msg.instance} step={reply.msg.step}", flush=True)
        except Exception as e:
            print(f"[{ctx.node_id}] VCBC send failed to {port}: {e}", flush=True)

    return msg  # return my own msg for self-delivery

def broadcast_certproposal(ctx, inst: int, proposer: str, value: str, proof: str, timeout_s: float = 2.0):
    req = helloworld_pb2.PRORequest(
        id=proposer,
        type="CERTPROPOSAL",
        instance=inst,
        proof=proof,
        value=value,
    )
    for port in Constants.PORTLIST[: ctx.n]:
        if port == ctx.port:
            continue
        try:
            get_stub(ctx, port).Propose(req, timeout=timeout_s)
            print(f"[{ctx.node_id}] -> CERTPROPOSAL sent to {port} inst={inst} proposer={proposer}", flush=True)
        except Exception as e:
            print(f"[{ctx.node_id}] CERTPROPOSAL send failed to {port}: {e}", flush=True)