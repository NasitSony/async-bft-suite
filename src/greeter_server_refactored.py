# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
import logging

import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import asyncio
import calendar;
import time;
import threading

import Constants

      


    

class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def __init__(self, node_id: str, port: int):
        """Initialize node-local state.

        This refactor keeps your existing RPC handlers, but:
        - allows running multiple nodes via CLI args (node_id/port)
        - replaces busy-wait loops with a Condition variable
        - adds a gRPC stub cache so nodes can talk to peers
        """
        # Allow runtime override instead of editing Constants.py per node
        Constants.ID = node_id
        Constants.PORT = port
        self.node_id = node_id
        self.port = port
        self._stubs = {}
        self._stub_lock = threading.Lock()

        # n, f, q2f1 are constants that don't need to be recomputed per RPC call, so we can compute them once in __init__
        self.n = Constants.N
        #self.f = Constants.FAULTY_NODES
        #self.q2f1 = 2 * self.f + 1
        n = len(Constants.PORTLIST[: self.n])
        self.f = min(Constants.FAULTY_NODES, (n - 1) // 3)
        self.q2f1 = 2 * self.f + 1
        print(f"[{self.node_id}] config: n={self.n} f={self.f} q2f1={self.q2f1} ports={Constants.PORTLIST[:self.n]}")

        # (instance, tag, round, value) -> set(sender_ids)
        self.certs = {}

        # instance -> decided value (or None)
        self.decided = {}  

        # Concurrency primitives (replace busy-wait loops)
        self._cv = threading.Condition()


        self.my_cert_sent = set()        # (instance) or (instance,value)
        self.certified_props = {}        # inst -> { proposer_id -> {"value":..., "proof":...} }

        # gRPC client cache for peer-to-peer sends
        self._stubs = {}

        # Node-local mutable state (avoid class-level dicts)
        self.preProcessMessage = {}
        self.preVoteMessage = {}
        self.mainVoteMessage = {}
        self.proposeMessage = {}
        self.outputMessage = {}
        self.coinMessage = {}
        self.classicPreProcessMessage = {}
        self.classicPreVoteMessage = {}
        self.classicMainVoteMessage = {}
        self.classicProposeMessage = {}
        self.classicCommitMessage = {}
        self.classicOutputMessage = {}
        self.classicCoinMessage = {}
        self.recommedationMessage = {}
        self.VABASignatures = {}
        self.ECoinShare = {}

        # Derive f safely (your Constants.FAULTY_NODES was sometimes larger than (n-1)//3)
        n = len(Constants.PORTLIST)
        self.f = min(Constants.FAULTY_NODES, (n - 1) // 3)

    def _get_stub_by_port(self, port: int):
        if port not in self._stubs:
            ch = grpc.insecure_channel(f"localhost:{port}")
            self._stubs[port] = helloworld_pb2_grpc.GreeterStub(ch)
        return self._stubs[port]
    
    def get_stub(self, port: int):
       with self._stub_lock:
          if port not in self._stubs:
             channel = grpc.insecure_channel(f"localhost:{port}")
             self._stubs[port] = helloworld_pb2_grpc.GreeterStub(channel)
          return self._stubs[port]

    def _notify(self):
        with self._cv:
            self._cv.notify_all()

    def _wait_for_key(self, dct, key: str):
        with self._cv:
            while key not in dct:
                self._cv.wait(timeout=1.0)
            return dct[key]

    def SayHello(self, request, context):
        print("Hello " + request.name)
        return helloworld_pb2.HelloReply(message="Hello, %s!" % request.name)
    
    def ElectLeader(self, request, context):
        #return super().ElectLeader(request, context)
        print("Elect reply")
        if request.id == Constants.ID:
           key = Constants.INSTANCE+str(request.view)
           if key not in self.ECoinShare:
               self.ECoinShare[key] = {"CShare":request.cshare}
               self._notify()
               return helloworld_pb2.ELeaderReply(id=Constants.ID, view = request.view, cshare=request.cshare)

        key = Constants.INSTANCE + str(request.view)
        ecoinshare = self._wait_for_key(self.ECoinShare, key)
        return helloworld_pb2.ELeaderReply(id=Constants.ID, view=request.view, cshare=ecoinshare["CShare"])
       
    

    def VCBC(self, request, context):
        print(f"[{self.node_id}] VCBC recv from {request.msg.id} inst={request.msg.instance} step={request.msg.step} value={request.msg.value}")

        self._on_vcbc(sender=request.msg.id, msg=request.msg)

        # keep your simulated share reply if you want, but no one should block waiting for it
        gmt = time.gmtime()
        time.sleep(Constants.SShare)
        reply = helloworld_pb2.mDict(
           instance=request.msg.instance,
           id=self.node_id,
           step=request.msg.step,
           ts=str(calendar.timegm(gmt)),
           value=request.msg.value
        )
        return helloworld_pb2.VCBCReply(msg=reply)    
       
    
    def ClassicVCBC(self, request, context):
        print("ClassicVCBC " + request.msg.id)

        # gmt stores current gmtime
        gmt = time.gmtime()
        #print(&quot;gmt:-&quot;, gmt)

        # ts stores timestamp
        self.ts = str(calendar.timegm(gmt) )
        time.sleep(Constants.SShare)
        #print(self.ts)
        message = helloworld_pb2.mDict( id=request.msg.id, step=request.msg.step, ts=str(calendar.timegm(gmt) ), value = request.msg.value)
        return helloworld_pb2.VCBCReply(msg=message)
    
    def pVCBC(self, request, context):
        print("pVCBC " + request.msg.id)

        # gmt stores current gmtime
        gmt = time.gmtime()
        #print(&quot;gmt:-&quot;, gmt)

        # ts stores timestamp
        self.ts = str(calendar.timegm(gmt) )
        time.sleep(Constants.SShare)
        #print(self.ts)
        message = helloworld_pb2.mDict( id=request.msg.id, step=request.msg.step, ts=str(calendar.timegm(gmt) ), value = request.msg.value)
        return helloworld_pb2.VCBCReply(msg=message)
    
    def ClassicPropose(self, request, context):
       

        if request.id == Constants.ID:
         key = Constants.INSTANCE+str(request.instance)
         if key not in self.classicProposeMessage:
            
             proposeMessage = {Constants.INSTANCE:request.instance, Constants.VALUE: request.value,Constants.PROOF: request.proof,"id":Constants.ID}
             self.classicProposeMessage[key] = proposeMessage
             
             return helloworld_pb2.ClassicPROReply(id=Constants.ID,type=request.type,instance=request.instance,proof=request.proof,value=request.value)
         
         


        while True:
                key = Constants.INSTANCE+str(request.instance)
                
                if key in self.classicProposeMessage:
                    proposeElement = self.classicProposeMessage[key] 
                   

                    #message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = preVoteElement[Constants.VALUE], justification = preVoteElement[Constants.JUSTIFICATION],  sign = preVoteElement[Constants.SIGN], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ClassicPROReply(id=Constants.ID, type="Propose", instance=proposeElement[Constants.INSTANCE], proof=proposeElement[Constants.PROOF],value=proposeElement[Constants.VALUE])  
       
    def ClassicCommit(self, request, context):
       

        if request.id == Constants.ID:
         key = Constants.INSTANCE+str(request.instance)
         if key not in self.classicCommitMessage:
            
             commitMessage = {Constants.INSTANCE:request.instance, "list": request.list, "id":Constants.ID}
             self.classicCommitMessage[key] = commitMessage
             
             return helloworld_pb2.ClassicCommitReply(id=Constants.ID,type=request.type,instance=request.instance,list=request.list)
         
         


        while True:
                key = Constants.INSTANCE+str(request.instance)
                
                if key in self.classicCommitMessage:
                    commitElement = self.classicCommitMessage[key] 
                   

                    #message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = preVoteElement[Constants.VALUE], justification = preVoteElement[Constants.JUSTIFICATION],  sign = preVoteElement["sign"], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ClassicCommitReply(id=Constants.ID, type=Constants.COMMIT, instance=commitElement[Constants.INSTANCE], list=commitElement["list"])  
     
    
    def _broadcast_certproposal(self, inst: int, proposer: str, value: str, proof: str):
        """
        Broadcast (value, QC proof) to all nodes.
        Uses Propose(PRORequest) with type='CERTPROPOSAL' so we don't steal Recommend().
        """
        req = helloworld_pb2.PRORequest(
           id=proposer,               # proposer node id
           type="CERTPROPOSAL",
           instance=inst,
           proof=proof,
           value=value,
        )

        for port in Constants.PORTLIST[: self.n]:
           if port == self.port:
              continue
           try:
             self.get_stub(port).Propose(req)
           except Exception as e:
            print(f"[{self.node_id}] CERTPROPOSAL send failed to {port}: {e}")
    
    
    def Propose(self, request, context):
       # --- Node-to-node certified proposal dissemination ---
       if getattr(request, "type", "") == "CERTPROPOSAL":
          inst = request.instance
          proposer = request.id
          value = request.value
          proof = request.proof

          self.certified_props.setdefault(inst, {})[proposer] = {"value": value, "proof": proof}
          print(f"[{self.node_id}] ✅ received CERTPROPOSAL inst={inst} proposer={proposer} value={value}")
          return helloworld_pb2.PROReply(yes="ack")

        # --- Client trigger path (your existing logic) ---
       inst = request.instance
       value = request.value
       print(f"[{self.node_id}] Propose trigger inst={inst} value={value}")

       key = Constants.INSTANCE + str(inst)
       self.proposeMessage[key] = {
          Constants.FROM: request.id,
          Constants.PROOF: getattr(request, "proof", ""),
          Constants.VALUE: value,
       }

       msg = helloworld_pb2.mDict(instance=inst, step=1, ts="1", value=value, id=self.node_id)
       req = helloworld_pb2.VCBCRequest(msg=msg)

       for port in Constants.PORTLIST[: self.n]:
          if port == self.port:
             continue
          try:
             self.get_stub(port).VCBC(req)
          except Exception as e:
            print(f"[{self.node_id}] VCBC send failed to {port}: {e}")

       # self-delivery
       self._on_vcbc(sender=self.node_id, msg=msg)

       return helloworld_pb2.PROReply(yes="yes")

    def _cert_add(self, inst: int, tag: str, step: int, value: str, sender: str) -> bool:
        key = (inst, tag, step, value)
        s = self.certs.setdefault(key, set())
        before = len(s)
        s.add(sender)
        after = len(s)
        return before < self.q2f1 and after >= self.q2f1

    def _on_vcbc(self, sender: str, msg):
        """
         Called whenever a VCBC message is received (including self-delivery).
         When a QC threshold is reached, if this node is the proposer for this instance,
         it broadcasts a CERTPROPOSAL(inst, value, proof) to all other nodes (via Propose RPC).
        """
        inst = msg.instance
        step = msg.step
        value = msg.value

        # Add sender to the cert set; fire exactly once when crossing quorum
        crossed = self._cert_add(inst, "VCBC", step, value, sender)
        if not crossed:
           return

        print(f"[{self.node_id}] ✅ VCBC cert ready inst={inst} step={step} value={value} (q={self.q2f1})")

        # Only broadcast "my cert" if this node actually has the client proposal for this instance
        pkey = Constants.INSTANCE + str(inst)
        if pkey not in self.proposeMessage:
            # This node didn't get the client input (in single-target-client mode)
            return

        my_value = self.proposeMessage[pkey][Constants.VALUE]
        if my_value != value:
           # The cert that formed isn't for my proposed value; ignore for "my cert broadcast"
           return

        # Broadcast only once per instance from this node
        if inst in self.my_cert_sent:
           return
        self.my_cert_sent.add(inst)

        # Build simulated QC proof from distinct signers
        cert_key = (inst, "VCBC", step, value)
        signers = sorted(self.certs.get(cert_key, set()))
        proof = f"QC|proposer={self.node_id}|inst={inst}|step={step}|signers=" + ",".join(signers)

        # Store locally as well
        self.certified_props.setdefault(inst, {})[self.node_id] = {"value": value, "proof": proof}

        print(f"[{self.node_id}] 📣 broadcasting CERTPROPOSAL inst={inst} proposer={self.node_id} value={value}")

        # Broadcast certified proposal to all nodes (decentralized dissemination)
        self._broadcast_certproposal(inst=inst, proposer=self.node_id, value=value, proof=proof)
    
    
    
    
    def Recommend(self, request, context):
        #print("inside recoomend")
        if request.id == Constants.ID:
           key = Constants.INSTANCE+str(request.instance)
           if key not in self.recommedationMessage:
               self.recommedationMessage[key] = {Constants.ID:request.id,"recomID":request.recomID,Constants.PROOF:request.proof,Constants.VALUE:request.value}
               self._notify()
               return helloworld_pb2.RECOReply(id=Constants.ID, type="Recommend", instance=request.instance,recomID=request.recomID,proof= request.proof,value=request.value)

        #self.recommendationCount += 1
        #self.recommendationList.add(request.type)
       
        #self.recommendationList.append()
        key = Constants.INSTANCE + str(request.instance)
        recommElement = self._wait_for_key(self.recommedationMessage, key)
        return helloworld_pb2.RECOReply(id=Constants.ID, type="Recommend", instance=request.instance, recomID=recommElement["recomID"], proof=recommElement[Constants.PROOF], value=recommElement[Constants.VALUE])
       
    


    def CollectProposal(self, request, context):
        key = Constants.INSTANCE + str(request.instance)
        proposeElem = self._wait_for_key(self.proposeMessage, key)
        return helloworld_pb2.CPROReply(cfrom=proposeElem[Constants.FROM], proof=proposeElem[Constants.PROOF], value=proposeElem[Constants.VALUE])



    def ClassicABBA(self, request, context):
        
        key = Constants.INSTANCE + str(request.message.instance)
        if key not in self.classicOutputMessage:
            outputElem = {Constants.INSTANCE:request.message.instance, Constants.ROUND: request.message.round, Constants.VALUE:1, Constants.JUSTIFICATION:request.message.justification,Constants.SIGN: "sg", Constants.TYPE: request.message.instance, "id":Constants.ID }
            self.classicOutputMessage[key] = outputElem
            

        
        if key in self.classicOutputMessage:
                outputElem = self.classicOutputMessage[key]
                messageType = outputElem[Constants.TYPE]
                if messageType == Constants.DECISION:
                   message = helloworld_pb2.messageABBA(instance=request.message.instance, round = 1, value = outputElem[Constants.VALUE], justification = "received",  sign = "sg", type = Constants.DECISION, id=Constants.ID)
                   return helloworld_pb2.ABBAReply(message=message)


        
        if request.message.type == Constants.PREPROCESS:

            if request.message.id == Constants.ID:
                key = Constants.INSTANCE+str(request.message.instance)
                if key not in self.classicPreProcessMessage:
                    self.classicPreProcessMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.VALUE:request.message.value, Constants.SIGN:request.message.sign}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = request.message.justification,  sign = request.message.sign, type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)
                 


            while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.classicPreProcessMessage:
                    preProcessElement = self.classicPreProcessMessage[key] 
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = preProcessElement[Constants.VALUE], justification = preProcessElement[Constants.JUSTIFICATION],  sign = preProcessElement[Constants.SIGN], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)

            
           
                
        if request.message.type == Constants.PREVOTE:
           
            if request.message.id == Constants.ID:
                key = Constants.INSTANCE+str(request.message.instance)
                if key not in self.classicPreVoteMessage:
                    self.classicPreVoteMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.VALUE:request.message.value, Constants.SIGN:request.message.sign}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = request.message.justification,  sign = request.message.sign, type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)
                
            
            while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.classicPreVoteMessage:
                    preVoteElement = self.classicPreVoteMessage[key] 
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = preVoteElement[Constants.VALUE], justification = preVoteElement[Constants.JUSTIFICATION],  sign = preVoteElement[Constants.SIGN], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)  
                

        if request.message.type == Constants.MAINVOTE:
           
             if request.message.id == Constants.ID:
                key = Constants.INSTANCE+str(request.message.instance)
                if key not in self.classicMainVoteMessage:
                    self.classicMainVoteMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.VALUE:request.message.value, Constants.SIGN:request.message.sign}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = request.message.justification,  sign = request.message.sign, type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)

            

             while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.classicMainVoteMessage:
                    mainVoteElement = self.classicMainVoteMessage[key] 
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = mainVoteElement[Constants.VALUE], justification = mainVoteElement[Constants.JUSTIFICATION],  sign = mainVoteElement[Constants.SIGN], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)   
                
        if request.message.type == Constants.DECISION:

            key = Constants.INSTANCE+str(request.message.instance)
            if key in self.classicOutputMessage:
                message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = "received",  sign = "sg", type = request.message.type, id=Constants.ID)
                return helloworld_pb2.ABBAReply(message=message)

            outputElem = {Constants.INSTANCE:request.message.instance, Constants.ROUND: request.message.round, Constants.VALUE:1, Constants.JUSTIFICATION:request.message.justification,Constants.SIGN: "sg", Constants.TYPE: request.message.type, "id":Constants.ID }

            self.classicOutputMessage[key] = outputElem
            message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = "received",  sign = "sg", type = request.message.type, id=Constants.ID)
            return helloworld_pb2.ABBAReply(message=message) 
        
        if request.message.type == "COIN":
            if request.message.id == Constants.ID:
                 key = Constants.INSTANCE+str(request.message.instance)
                 if key not in self.classicCoinMessage:
                     self.classicCoinMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.TYPE:request.message.type}
                     message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = request.message.justification,  sign = "sg", type = request.message.type, id=Constants.ID)
                     return helloworld_pb2.ABBAReply(message=message)
                 

            while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.classicCoinMessage:
                    self.classicCoinMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.TYPE:request.message.type}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = self.classicCoinMessage[key][Constants.JUSTIFICATION],  sign = "sg", type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)

      


    
    def ABBA(self, request, context):
        
        key = Constants.INSTANCE + str(request.message.instance)
        if key not in self.outputMessage:
            outputElem = {Constants.INSTANCE:request.message.instance, Constants.ROUND: request.message.round, Constants.VALUE:1, Constants.JUSTIFICATION:request.message.justification,Constants.SIGN: "sg", Constants.TYPE: request.message.instance, "id":Constants.ID }
            self.outputMessage[key] = outputElem
            

        
        if key in self.outputMessage:
                outputElem = self.outputMessage[key]
                messageType = outputElem[Constants.TYPE]
                if messageType == Constants.DECISION:
                   message = helloworld_pb2.messageABBA(instance=request.message.instance, round = 1, value = outputElem[Constants.VALUE], justification = "received",  sign = "sg", type = Constants.DECISION, id=Constants.ID)
                   return helloworld_pb2.ABBAReply(message=message)


        
        if request.message.type == Constants.PREPROCESS:

            if request.message.id == Constants.ID:
                key = Constants.INSTANCE+str(request.message.instance)
                if key not in self.preProcessMessage:
                    self.preProcessMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.VALUE:request.message.value, Constants.SIGN:request.message.sign}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = request.message.justification,  sign = request.message.sign, type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)
                 


            while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.preProcessMessage:
                    preProcessElement = self.preProcessMessage[key] 
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = preProcessElement[Constants.VALUE], justification = preProcessElement[Constants.JUSTIFICATION],  sign = preProcessElement[Constants.SIGN], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)

            
           
                
        if request.message.type == Constants.PREVOTE:
           
            if request.message.id == Constants.ID:
                key = Constants.INSTANCE+str(request.message.instance)
                if key not in self.preVoteMessage:
                    self.preVoteMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.VALUE:request.message.value, Constants.SIGN:request.message.sign}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = self.preVoteMessage[key][Constants.VALUE], justification = request.message.justification,  sign = request.message.sign, type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)
                
            
            while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.preVoteMessage:
                    preVoteElement = self.preVoteMessage[key] 
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = preVoteElement[Constants.VALUE], justification = preVoteElement[Constants.JUSTIFICATION],  sign = preVoteElement[Constants.SIGN], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)  
                

        if request.message.type == Constants.MAINVOTE:
           
             if request.message.id == Constants.ID:
                key = Constants.INSTANCE+str(request.message.instance)
                if key not in self.mainVoteMessage:
                    self.mainVoteMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.VALUE:request.message.value, Constants.SIGN:request.message.sign}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = self.mainVoteMessage[key][Constants.VALUE], justification = request.message.justification,  sign = request.message.sign, type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)

            

             while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.mainVoteMessage:
                    mainVoteElement = self.mainVoteMessage[key] 
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = mainVoteElement[Constants.VALUE], justification = mainVoteElement[Constants.JUSTIFICATION],  sign = mainVoteElement[Constants.SIGN], type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)   
                
        if request.message.type == Constants.DECISION:

            key = Constants.INSTANCE+str(request.message.instance)
            if key in self.outputMessage:
                message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = "received",  sign = "sg", type = request.message.type, id=Constants.ID)
                return helloworld_pb2.ABBAReply(message=message)

            outputElem = {Constants.INSTANCE:request.message.instance, Constants.ROUND: request.message.round, Constants.VALUE:1, Constants.JUSTIFICATION:request.message.justification,Constants.SIGN: "sg", Constants.TYPE: request.message.type, "id":Constants.ID }

            self.outputMessage[key] = outputElem
            message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = "received",  sign = "sg", type = request.message.type, id=Constants.ID)
            return helloworld_pb2.ABBAReply(message=message) 
        
        if request.message.type == "COIN":
            if request.message.id == Constants.ID:
                 key = Constants.INSTANCE+str(request.message.instance)
                 if key not in self.coinMessage:
                     self.coinMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.TYPE:request.message.type}
                     message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = request.message.justification,  sign = "sg", type = request.message.type, id=Constants.ID)
                     return helloworld_pb2.ABBAReply(message=message)
                 

            while True:
                key = Constants.INSTANCE+str(request.message.instance)
                if key in self.coinMessage:
                    self.coinMessage[key] = {Constants.JUSTIFICATION:request.message.justification,Constants.TYPE:request.message.type}
                    message = helloworld_pb2.messageABBA(instance=request.message.instance, round = request.message.round, value = request.message.value, justification = self.coinMessage[key][Constants.JUSTIFICATION],  sign = "sg", type = request.message.type, id=Constants.ID)
                    return helloworld_pb2.ABBAReply(message=message)

            


def serve():
    port = str(Constants.PORT)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


async def serve() -> None:
    port = str(Constants.PORT)
    server = grpc.aio.server()
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    #listen_addr = "[::]:50053"
    server.add_insecure_port("[::]:" + port)
    #server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", str(Constants.PORT))
    await server.start()
    await server.wait_for_termination()




def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="Node id string, e.g. id1")
    ap.add_argument("--port", type=int, required=True, help="Listen port for this node")
    ap.add_argument("--max_workers", type=int, default=64)
    args = ap.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=args.max_workers))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(node_id=args.id, port=args.port), server)
    server.add_insecure_port(f"[::]:{args.port}")
    server.start()
    print(f"Server started: id={args.id} port={args.port}")
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    main()
