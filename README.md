# Grid07: Cognitive Routing & RAG

This repository contains the Grid07 AI Engineering assignment: semantic routing, autonomous content generation, and a Deep Context RAG combat engine.

## Setup & Execution

1. Install dependencies: `pip install -r requirements.txt`
2. Add your API key: Copy `.env.example` to `.env` and insert your Groq key.
3. Run the full pipeline: `python main.py`

*(Execution logs for all three phases are saved in `execution_logs.md`)*

---

## 1. Semantic Routing (Phase 1)
Incoming posts are routed only to bots that "care" about the topic using **Cosine Similarity**.
* **Embeddings:** Bot personas and incoming posts are converted into vectors using `all-MiniLM-L6-v2` via an in-memory ChromaDB instance.
* **Matching:** The system calculates the semantic distance between the post and each persona. 
* **Calibration:** Any bot with a similarity score > `0.20` is triggered. (This threshold is specifically calibrated for MiniLM's semantic variance when comparing short posts to long persona descriptions).

---

## 2. LangGraph Node Structure (Phase 2)
The autonomous content engine operates as a linear 3-node LangGraph state machine passing a single `GraphState` dictionary:
* **Node 1 (Decide Search):** The LLM reviews its persona and outputs a targeted search query (enforced via Pydantic structured output).
* **Node 2 (Web Search):** A deterministic LangChain `@tool` fetches real-world headlines using strict regex word-boundary matching.
* **Node 3 (Draft Post):** The LLM synthesizes its persona, its original reasoning, and the news into a strict 280-character JSON output.

---

## 3. Prompt Injection Defense (Phase 3)
To defend against jailbreaks deep within a comment thread, I implemented a **Two-Layer (Defense-in-Depth)** architecture using In-Context RAG:
* **Layer 1 (Pre-screen Sandbox):** The human's reply is scanned against a regex dictionary of known injection patterns. If flagged, the payload is wrapped in a literal warning block (`INJECTION ATTEMPT DETECTED`), isolating it from system execution.
* **Layer 2 (System Hardening):** The System Prompt is fortified with strict `[SECURITY RULES]`, explicitly commanding the LLM to ignore identity-change requests and attack the argument's logic instead.
* **In-Context RAG:** The thread history is structured sequentially (`[HUMAN]: ... [BOT]: ...`), giving the LLM full conversational memory to build a grounded defense without needing a vector database.
