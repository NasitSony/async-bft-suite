
🚀 Asynchronous BFT Protocol Framework

Quorum-Based Asynchronous Byzantine Fault-Tolerant Consensus Framework


🧠 Overview

Async-BFT Suite is a runnable distributed system framework for simulating and analyzing Byzantine fault-tolerant consensus under asynchronous conditions.
It models how nodes reach agreement in the presence of:
- adversarial (malicious) behavior
- network delays and message reordering
- partial failures

The system integrates cryptographic verification, quorum-based certification, and asynchronous agreement protocols into a unified execution pipeline.

⚙️ Protocol Flow
Client → VCBC → Certificate → CERTPROPOSAL → BITVEC → Support Set → ABBA → Decision

Flow Explanation
- Client → VCBC
  Initiates a value broadcast using Verifiable Consistent Broadcast

- VCBC → Certificate
  Nodes validate and form a quorum certificate (2f+1)

- Certificate → CERTPROPOSAL
  Certified values are proposed for consensus

- CERTPROPOSAL → BITVEC
  Nodes exchange support using bit vectors

- BITVEC → Support Set
  Aggregation of node support for candidate values

- Support Set → ABBA
  Binary agreement resolves final decision

- ABBA → Decision
  System reaches fault-tolerant consensus

🔐 Cryptographic & Trust Model
- Quorum-based certification (2f+1)
  Guarantees correctness with up to f Byzantine nodes

- Integrity verification (e.g., SHA-based hashing / signatures)
  Ensures messages cannot be tampered with

- Tamper-resistant pipeline
  Certificates and proposals enforce verifiable state transitions

⚙️ Key Features

- Fully decentralized (leaderless)
  Eliminates single point of failure

- Asynchronous execution model
  Handles unpredictable network delays and message ordering

- Quorum-based trust model
  Ensures agreement despite adversarial nodes

- Binary Agreement (ABBA)
  Finalizes decisions using randomized techniques (simulated common coin)

- Fault injection support (planned / implemented)
  Simulates Byzantine nodes, delays, and dropped messages

🧪 What This System Demonstrates

This framework enables:
- Evaluation of consensus correctness under failure
- Simulation of Byzantine node behavior
- Analysis of quorum formation and agreement dynamics
- Observability into message flow and decision-making  
  

Supports multiple protocol designs including:
- Prioritized MVBA (pMVBA)
- Cachin MVBA
- VABA
  
Designed to explore correctness under failures, message coordination, and consensus without synchrony assumptions.
🧠 Key Highlights
- ⚙️ End-to-end implementation of BFT protocol components
- 🔧 Refactoring into clean, modular architecture
- 🧩 Separation of network (gRPC) and protocol logic
- 🔁 Multi-node asynchronous message passing
- 🧪 Designed for fault injection and correctness testing (in progress)


👉 Transition:
- From monolithic implementation
- To reusable protocol framework



- Asynchronous communication model
- Quorum-based decisions (≥ 2f+1)
- Designed for adversarial/failure scenarios

🚧 Current Status
- ✅ Initial protocol implementations complete
- ✅ Refactoring into modular framework in progress
- 🚧 Fault injection & testing framework planned

🎯 Goal

Bridge research-grade BFT protocols with production-style system design, focusing on:
- correctness under failures
- modular protocol composition
- real-world distributed behavior

👨‍💻 Author
- Distributed systems engineer focused on Byzantine fault tolerance, consensus protocols, and system correctness.
