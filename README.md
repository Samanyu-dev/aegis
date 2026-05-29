# AEGIS — Autonomous Enterprise Intelligence Operating System

> **Bright Data "Web Data UNLOCKED" Hackathon (May 2026)**
> **Tracks**: Security & Compliance (Primary) // GTM Intelligence // Finance & Market Intelligence
> **Live Console URL**: `http://localhost:3000` // **FastAPI Server URL**: `http://localhost:8000`

---

## 1. Executive Slogan & Core Vision
AEGIS is an **AI-Native Autonomous Enterprise Intelligence Operating System** engineered to monitor open-web indices, public subcontractors code repositories, corporate logs, and GTM pricing directories. 

AEGIS is **not a chatbot**. It is an event-driven multi-agent network that bridges the gap between passive reporting and autonomous action. 
*   **PATROL & UNLOCK**: Patrols the live web using rotating proxies to extract high-fidelity signals.
*   **COGNIZE**: Maintains semantic profiles in a persistent, evolving relationship knowledge graph.
*   **SYNTHESIZE**: Renders structured executive reports, maps competitor moves, and rates threat risks.
*   **DISPATCH**: Fires active automation pipelines when risk thresholds exceed severity indexes.

The design is engineered to feel like **Palantir meets Bloomberg Terminal** — high-performance, dark-themed, and cinematic.

---

## 2. Technical System Architecture

### 2.1 Data Flow & Services Mapping
```
                                 +-----------------------+
                                 |  NEXT.JS FRONTEND UI  | <----------+
                                 |  (Command Dashboard)  |            |
                                 +-----------+-----------+            |
                                             |                        | SSE (Server-Sent Events)
                                             | GET /POST              | 
                                             v                        |
                                 +-----------------------+            |
                                 |  FASTAPI WEB SERVER   | -----------+
                                 +-----------+-----------+
                                             |
                                             v (Graph Invoke)
+--------------------------------------------|--------------------------------------------+
|  packages/agents/graph.py                  |                                            |
|                                            v                                            |
|    +---------------------------------------+---------------------------------------+    |
|    |                             SCOUT NODE (Scouts links)                         |    |
|    |  - Runs dynamic queries via Bright Data SERP API                              |    |
|    |  - Streams live EventSource telemetry logs                                    |    |
|    +---------------------------------------+---------------------------------------+    |
|                                            |                                            |
|                                            v (Found URLs)                               |
|    +---------------------------------------+---------------------------------------+    |
|    |                          INVESTIGATE NODE (Crawls & Extracts)                 |    |
|    |  - Scrapes target pages using Bright Data Web Unlocker                        |    |
|    |  - Connects over CDP to Bright Data Scraping Browser for dynamic JS           |    |
|    |  - Mapped entities extracted using AI/ML API (Mistral trials)                 |    |
|    |  - Queries Cognee Semantic Graph to pull historical intelligence profiles    |    |
|    +---------------------------------------+---------------------------------------+    |
|                                            |                                            |
|                                            v (Indicators list)                          |
|    +---------------------------------------+---------------------------------------+    |
|    |                          SYNTHESIZE NODE (Scores & dispatches)                |    |
|    |  - Generates executive report and risk score via AI/ML API (GPT-4o)            |    |
|    |  - Ingests entity profiles persistently into Cognee memory                    |    |
|    |  - Fires HIGH_RISK_DETECTED webhook triggers to TriggerWare                   |    |
|    |  - Commits runs, signals, and nodes to database (PostgreSQL/SQLite)           |    |
|    +-------------------------------------------------------------------------------+    |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Deep-Dive Partner Implementations

### 3.1 Bright Data (SERP API + Web Unlocker + Scraping Browser)
*   **SERP API Integration (`packages/shared/bright_data.py`)**: Leverages your active search credentials. It targets the endpoint `https://api.brightdata.com/request` on zone `aegis_1` and requests `raw` HTML. A custom regex-based links extractor cleans Google redirection parameters (`/url?q=LINK`), filters out internal Google resources, and **reconstructs organic live URLs and titles** dynamically.
*   **Web Unlocker (`packages/shared/bright_data.py`)**: Routes GET requests through the superproxy network (`brd.superproxy.io:22225`) to bypass Cloudflare, bot barriers, and captchas. If credentials are left blank, it falls back to standard HTTP, and if blocked, injects highly-realistic context-aware mocks (e.g. Anthropic hiring, exposed AWS keys).
*   **Scraping Browser (`packages/shared/bright_data.py`)**: Links Playwright to Bright Data's remote headless Chromium cluster (`wss://brd.superproxy.io:9222`) over Chrome DevTools Protocol (CDP) to evaluate dynamic client-side JavaScript sites.

### 3.2 Cognee (Persistent Entity Memory)
*   **Semantic Graphing (`packages/memory/cognee_client.py`)**: Mapped in `INVESTIGATE` and `SYNTHESIZE` nodes. Before running a search, Cognee is queried using `INSIGHTS` searches to recall historical facts. After a run completes, newly discovered entities are added via `cognee.add` and persistent relationship graphs are compiled via `cognee.cognify()`.
*   **Dual-Write Fallback**: If `COGNEE_API_KEY` is not provided, the client enters a simulated mode and routes structured nodes and edges to your local database `memory_nodes` table, guaranteeing that **your Memory Graph renders beautifully under any state!**

### 3.3 TriggerWare (Automated Action Pipelines)
*   **Automated Webhook triggers (`packages/workflows/trigger_client.py`)**: When threat scores exceed `7.0/10.0`, the Synthesize node dispatches the `HIGH_RISK_DETECTED` event payload containing your structured report. 
*   **Smart Key Resolver**: If `TRIGGERWARE_WEBHOOK_URL` in `.env` is populated with a raw webhook key ID (e.g. `TjKdmz_...`), the trigger client dynamically strips spaces and prefixes it with the standard `https://app.triggerware.ai/webhooks/` endpoint, eliminating URL formatting parse failures.

### 3.4 AI/ML API (Multi-Model Smart Routing & Fallback Trial Engine)
*   **Smart Model Routing (`packages/agents/ai_client.py`)**: 
    *   **Mistral-7b-instruct** (Fast / Low Latency): Deployed in the Investigate node to parse raw HTML and structure findings as clean JSON.
    *   **GPT-4o** (Strong Reasoning): Deployed in the Synthesize node to digest all search logs and output the final briefing.
*   **404 Model Not Found Fallback Trial Loop**: To make entity extraction bulletproof against model name variations or temporary downtime on the AI/ML API, `ai_client.py` loops through a list of candidate models: **`["mistralai/Mistral-7B-Instruct-v0.2", "gpt-4o-mini", "gpt-4o"]`**. If a model fails or throws a 404, the engine instantly retries with the next candidate in the queue, ensuring zero pipeline crashes.

---

## 4. Cinematic Command Dashboard Manual

The dashboard interface (`http://localhost:3000/dashboard`) is divided into distinct operational panels:

1.  **Top Control Deck**: Input box to target companies (e.g. OpenAI, Anthropic) and select scanning focus parameters (`Security Risk`, `Hiring Signal`, `Pricing Shift`) that are passed directly to the LangGraph agents.
2.  **Cognitive Reasoning Stream (Center-Left)**: styled as an auto-scrolling hacker terminal. It displays live Server-Sent Events (SSE) progress streams (`[SCOUT]`, `[INVESTIGATE]`, `[SYNTHESIZE]`) straight from the agent execution loop.
3.  **Live Threat Beacons (Left)**: Pulsing radar alert widgets highlighting extracted signals in real time, color-coded by severity (Amber for GTM, Red for security credential exposures).
4.  **Memory Knowledge Graph (Center-Bottom)**: An interactive glowing SVG node-edge connection map representing semantic relationships. You can pan, zoom, click nodes to view sidebar property cards, and drag nodes to re-organize the layout.
5.  **Executive Briefing (Right)**: The final compiled assessment. Renders a glowing radial threat dial, professional GTM recommendations, scrape source links, and a **Download button** to save the full report as a structured Markdown file.
6.  **TriggerWare dispatches (Bottom-Left)**: Logs triggered automation webhooks and delivery responses in real time.
7.  **Historical Scans (Bottom-Right)**: Mapped records pulled directly on mount from your database.

---

## 5. Setup & Running Instructions

### 5.1 Environment Configuration (`.env`)
A prepared [.env](file:///Users/apple/Desktop/aegis/.env) file is located at your project root. Simply open it and fill in your keys:
```env
# Bright Data Credentials
BRIGHT_DATA_SERP_API_KEY=your_brightdata_serp_api_token
BRIGHT_DATA_SCRAPING_BROWSER_URL=wss://brd-customer-XXXX-zone-XXXX:PASSWORD@brd.superproxy.io:9222
BRIGHT_DATA_WEB_UNLOCKER_URL=  # Leave blank to engage local scraper backup

# AI/ML API Credentials (Redeem your hackathon coupon on aimlapi.com)
AIML_API_KEY=your_aiml_api_key_here
AIML_API_BASE_URL=https://api.aimlapi.com/v1

# Cognee Credentials
COGNEE_API_KEY=  # Leave blank to engage SQLite semantic graph fallback

# TriggerWare Credentials
TRIGGERWARE_WEBHOOK_URL=your_triggerware_webhook_url_or_key_id

# Optional PostgreSQL Database (defaults to a local SQLite 'aegis.db' inside apps/backend if left empty)
DATABASE_URL=
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5.2 Starting the App Locally (Faster Debugging)
To run the backend and frontend locally using your host Python and Node environments:

#### Terminal 1 — FastAPI Backend:
```bash
cd /Users/apple/Desktop/aegis/apps/backend
pip3 install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Terminal 2 — Next.js Frontend:
```bash
cd /Users/apple/Desktop/aegis/apps/frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser to launch the command console!

### 5.3 Starting the App with Docker Compose
If you prefer running a fully containerized network with PostgreSQL and pgvector:
```bash
docker-compose up --build
```
*   **Command Dashboard**: `http://localhost:3000`
*   **FastAPI API Swagger Docs**: `http://localhost:8000/docs`
*   **Postgres Database**: `localhost:5432`

---

## 6. Hackathon Judging Tracks Alignment

AEGIS is built to excel across three distinct tracks:

1.  **Security & Compliance (Primary)**: Mapped inside the `BREACH_SIGNAL_FOUND` event parser. Tracks exposed corporate credentials and database tokens on open subcontractor repositories, generates secure response recommendations, and dispatches direct `HIGH_RISK_DETECTED` dispatches to TriggerWare nodes.
2.  **GTM Intelligence**: Monitors competitive recruitment growths, tracking active roles (e.g. Anthropic's 430 compliance roles surge), locating strategic executive hiring re-allocations, and mapping organizational adjustments.
3.  **Finance & Market Intelligence**: Scrapes competitor blogs and documentation to track strategic pricing model reductions (e.g., Mistral lowering CodeStral API pricing by 20%), alerting finance teams of competitive pricing pivots.
