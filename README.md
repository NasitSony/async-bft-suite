
🚀 Asynchronous BFT Protocol Framework

Implementation and ongoing refactoring of asynchronous Byzantine Fault Tolerant (BFT) consensus protocols into a modular, protocol-driven distributed system framework.

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


🏗️ Architecture
node_server.py   → RPC handlers (network layer)
node_client.py   → outbound communication
protocol/
  pmvba.py
  mvba.py
  vaba.py

👉 Transition:
- From monolithic implementation
- To reusable protocol framework

🔄 Protocol Flow (Generalized)
Propose → Broadcast → Vote/Recommend → Decide

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
