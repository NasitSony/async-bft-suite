# async-bft-suite
🚀 Asynchronous BFT Protocol Framework (pMVBA Prototype)

A modular distributed systems framework implementing asynchronous Byzantine Fault Tolerant (BFT) protocols, including a prototype of Prioritized MVBA (pMVBA).

Designed to explore correctness under failures, message coordination, and consensus without synchrony assumptions.

🧠 Key Features

⚙️ gRPC-based node communication layer

🧩 Protocol-driven architecture (clean separation of networking and logic)

🔁 Multi-node message passing simulation

📦 Support for:

pMVBA (in progress)

Cachin MVBA (planned)

VABA (planned)

🧪 Designed for fault injection and adversarial testing (upcoming)

🏗️ Architecture
node_server.py   → RPC handlers (network layer)
node_client.py   → outbound communication
protocol/
  pmvba.py       → protocol logic (core)

👉 Clean separation:

gRPC handles message transport

Protocol classes handle consensus logic

🔄 Protocol Flow (Simplified)
Propose → VCBC → Recommend → Decide

- Nodes exchange messages via RPC
- Decisions are made based on quorum (≥ 2f+1)
- No reliance on synchrony assumptions

🚧 Current Status
- ✅ Communication layer complete
- ✅ PMVBA protocol skeleton implemented
- 🚧 Full protocol logic in progress
- 🚧 Fault injection & testing (planned)

🎯 Goal

To bridge research-grade BFT protocols with practical distributed system implementations, focusing on:
- correctness under failures
- modular protocol design
- real-world system behavior

👨‍💻 Author
- Built as part of research and system design work in distributed systems and Byzantine consensus.  
