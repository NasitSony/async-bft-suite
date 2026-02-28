# src/server.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # allow imports from repo root

from concurrent import futures
import argparse
import time
import calendar
import grpc

from proto import helloworld_pb2
from proto import helloworld_pb2_grpc
from config import constants as Constants


from .context import NodeContext
from . import transport
from . import vcbc_cert
from . import bitvec
from . import abba_start
from . import abba
from . import mvba

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def __init__(self, ctx: NodeContext):
        self.ctx = ctx
        ctx.mvba_on_aba_decide = lambda inst, b: mvba.on_aba_decide(ctx, inst, b)
        

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message=f"Hello, {request.name}!")

    def Propose(self, request, context):
        rtype = (getattr(request, "type", "") or "").strip()

        if rtype == "BITVEC":
           get_stub = lambda port: transport.get_stub(self.ctx, port)

           bitvec.on_bitvec(
              self.ctx,
              sender=request.id,
              inst=request.instance,
              bitstr=request.value,
              abba_start_cb=lambda inst, S: abba_start.start_abba_if_ready(
              self.ctx, inst, S, get_stub=lambda port: transport.get_stub(self.ctx, port)
            )
)
           return helloworld_pb2.PROReply(yes="ack_bitvec")


        # node-to-node CERTPROPOSAL receive
        if rtype == "CERTPROPOSAL":
            vcbc_cert.on_certproposal(
                self.ctx,
                proposer=request.id,
                inst=request.instance,
                value=request.value,
                proof=request.proof,
            )
            return helloworld_pb2.PROReply(yes="ack_certproposal")

        # client start path
        if rtype == "":
            if request.id != "client":
                print(f"[{self.ctx.node_id}] ⚠️ ignoring non-client Propose empty type from={request.id}", flush=True)
                return helloworld_pb2.PROReply(yes="ignored")

            inst = request.instance
            value = request.value
            print(f"[{self.ctx.node_id}] Propose trigger inst={inst} value={value} (from=client)", flush=True)

            # store local input
            key = Constants.INSTANCE + str(inst)
            self.ctx.proposeMessage[key] = {
                Constants.FROM: request.id,
                Constants.PROOF: getattr(request, "proof", ""),
                Constants.VALUE: value,
            }

            # IMPORTANT: if QC formed before input arrived, broadcast now (late fix)
            vcbc_cert.try_broadcast_my_cert_if_ready(self.ctx, inst, step=1, value=value)

            # broadcast VCBC
            my_msg = transport.broadcast_vcbc(self.ctx, inst=inst, step=1, value=value)

            # self-delivery
            vcbc_cert.on_vcbc(self.ctx, sender=self.ctx.node_id, msg=my_msg)

            return helloworld_pb2.PROReply(yes="yes")

        print(f"[{self.ctx.node_id}] Propose recv type={rtype!r} ignored in upto-cert mode", flush=True)
        return helloworld_pb2.PROReply(yes="ignored")

    
    def ABBA(self, request, context):
       msg = request.message
       inst = msg.instance
       rnd = msg.round
       mtype = msg.type
       sender = msg.id
       bit = msg.value

       print(
         f"[{self.ctx.node_id}] 📨 ABBA "
         f"| inst={inst} "
         f"| r={rnd} "
         f"| type={mtype} "
         f"| from={sender} "
         f"| bit={bit} "
         f"| just={msg.justification}",
         flush=True
       )

       # ✅ LOG RECEIPT HERE (before storing / before on_abba_message)
       if mtype == Constants.PREPROCESS:
          print(f"[{self.ctx.node_id}] ✅ PREPROCESS RECEIVED inst={inst} r={rnd} from={sender} bit={bit}", flush=True)


       get_stub = lambda port: transport.get_stub(self.ctx, port)

       abba.on_abba_message(
          ctx=self.ctx,
          get_stub=get_stub,
          inst=msg.instance,
          rnd=msg.round,
          mtype=msg.type,
          sender=msg.id,
          bit=int(msg.value),
        )
       return helloworld_pb2.ABBAReply(message=msg)    
    
    def VCBC(self, request, context):
        print(f"[{self.ctx.node_id}] VCBC recv from {request.msg.id} inst={request.msg.instance} step={request.msg.step} value={request.msg.value}", flush=True)

        # deliver
        vcbc_cert.on_vcbc(self.ctx, sender=request.msg.id, msg=request.msg)

        # reply
        gmt = time.gmtime()
        time.sleep(getattr(Constants, "SShare", 0.0))
        reply = helloworld_pb2.mDict(
            instance=request.msg.instance,
            id=self.ctx.node_id,
            step=request.msg.step,
            ts=str(calendar.timegm(gmt)),
            value=request.msg.value
        )
        return helloworld_pb2.VCBCReply(msg=reply)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--max_workers", type=int, default=64)
    args = ap.parse_args()

    # runtime override
    Constants.ID = args.id
    Constants.PORT = args.port

    ctx = NodeContext(node_id=args.id, port=args.port)
    ctx.init_quorum()

    print(f"[{ctx.node_id}] config: n={ctx.n} f={ctx.f} q2f1={ctx.q} ports={Constants.PORTLIST[:ctx.n]}", flush=True)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=args.max_workers))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(ctx), server)
    server.add_insecure_port(f"[::]:{args.port}")
    server.start()
    print(f"Server started: id={args.id} port={args.port}", flush=True)
    server.wait_for_termination()

if __name__ == "__main__":
    main()