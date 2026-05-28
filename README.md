# AEGIS — Autonomous Enterprise Intelligence Operating System

> **Web Data UNLOCKED Hackathon (May 2026)**
> **Tracks**: Security & Compliance (Primary) // GTM Intelligence // Finance & Market Intelligence

---

## 1. Project Slogan & Vision
AEGIS is an **AI-Native Autonomous Enterprise Intelligence Operating System** built to monitor corporate directories, news indexes, public repositories, and pricing interfaces in real time. 

AEGIS is **not a chatbot**. It is a continuous, self-directing intelligence pipeline that:
- **Scans & Unlocks**: Searches the live web and bypasses scraper protections.
- **Cognifies**: Retains discovered entities inside an evolving persistent relationship graph.
- **Synthesizes**: scores threat vectors and maps competitive market pivots.
- **Dispatches**: Triggers automated webhooks to corporate operations when risks exceed severity thresholds.

---

## 2. System Architecture Diagram

```
+------------------------------------------------------------------------+
|                               FRONTEND                                 |
|   +----------------------------------------------------------------+   |
|   |         Next.js 15 command center dashboard (Port 3000)        |   |
|   |   - Live Cognition Terminal    - Pulsing Live Signal Beacons   |   |
|   |   - Interactive Memory Graph   - Threat Score radial gauge     |   |
|   +----------------------------------------------------------------+   |
+-----------------------------------^------------------------------------+
                                    |
                                    | SSE (Server-Sent Events)
                                    |
+-----------------------------------|------------------------------------+
|                               BACKEND                                  |
|   +-------------------------------+      +-------------------------+   |
|   |  FastAPI server (Port 8000)   | ---> |   SQLAlchemy Engine     |   |
|   +---------------+---------------+      |   (Postgres/SQLite)     |   |
|                   |                      |   - investigations      |   |
|                   |                      |   - signals             |   |
|                   v (ainvoke)            |   - workflow_events     |   |
|     +---------------------------+        |   - memory_nodes        |   |
|     |  LangGraph Agent Pipeline |        +-------------------------+   |
|     |  SCOUT                    |                                      |
|     |    | (Bright Data SERP)   |                                      |
|     |    v                      |                                      |
|     |  INVESTIGATE              |                                      |
|     |    | (Web Unlocker)       |                                      |
|     |    | (AI/ML API Mistral)  |                                      |
|     |    | (Cognee Context)     |                                      |
|     |    v                      |                                      |
|     |  SYNTHESIZE               |                                      |
|     |    | (AI/ML API GPT-4o)   |                                      |
|     |    | (Cognee remember)    |                                      |
|     |    | (TriggerWare hook)   |                                      |
|     +---------------------------+                                      |
+------------------------------------------------------------------------+
```

---

## 3. Partner Integrations

### 3.1 Bright Data (SERP API + Web Unlocker + Scraping Browser)
- **SERP API**: Deployed inside the `SCOUT` agent node. It performs concurrent, multi-query queries to map dynamic search indices for competitors, news, and repository exposures.
- **Web Unlocker**: Deployed inside the `INVESTIGATE` agent node. It crawls discovered target resources using advanced, rotating superproxies to safely unlock and extract information without bot/captcha blockages.
- **Scraping Browser**: Deployed over Playwright CDP integration to scrape dynamic, client-side JS single-page sites like SaaS pricing consoles.

### 3.2 Cognee (Persistent Entity Memory)
- Deployed inside the `INVESTIGATE` and `SYNTHESIZE` nodes. Before every research scan, Cognee is queried using `INSIGHTS` semantic queries to recall past context about the target. After every scan, newly discovered companies, executives, and threat profiles are ingested via `cognee.add` and persistent graphs are constructed via `cognee.cognify()`.

### 3.3 TriggerWare (Automated Action Pipelines)
- Deployed inside the `SYNTHESIZE` node. Translates threat telemetry into automated dispatches. If a critical credential leak is discovered or competitive metrics score > 7.0/10.0, the backend immediately fires dispatches to TriggerWare webhooks, automating security responses or slack notifications.

### 3.4 AI/ML API (Multi-Model Smart Routing)
- Rather than a single model system, AEGIS implements cost/accuracy smart routing:
  - **Mistral-7b-instruct** (Fast / Structured): Scans scraped HTML and outputs clean JSON arrays of found entities and signals.
  - **GPT-4o** (Strong Reasoning): Combines scrape logs and past memory context to generate comprehensive risk assessments and response recommendations.

---

## 4. Setup & Running Instructions

### 4.1 Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose
- API Keys for Bright Data, AI/ML API, Cognee, and TriggerWare.

### 4.2 Configuration (.env)
Create a `.env` file in the root directory:
```env
# Bright Data Credentials
BRIGHT_DATA_SERP_API_KEY=your_serp_key_here
BRIGHT_DATA_WEB_UNLOCKER_URL=http://brd-customer-XXXX:PASSWORD@brd.superproxy.io:22225
BRIGHT_DATA_SCRAPING_BROWSER_URL=wss://brd-customer-XXXX:PASSWORD@brd.superproxy.io:9222

# AI/ML API Credentials
AIML_API_KEY=your_aimlapi_key_here
AIML_API_BASE_URL=https://api.aimlapi.com/v1

# Cognee Credentials
COGNEE_API_KEY=your_cognee_key_here

# TriggerWare Credentials
TRIGGERWARE_WEBHOOK_URL=your_webhook_url_here

# Optional: PostgreSQL Database (Defaults to local SQLite aegis.db if empty)
DATABASE_URL=postgresql://postgres:password@db:5432/aegis
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4.3 Spin up with Docker Compose
Run the following command in the root folder to boot Postgres, the FastAPI backend, and the Next.js frontend:
```bash
docker-compose up --build
```

Access the system:
- **Command Dashboard**: `http://localhost:3000`
- **FastAPI API Swagger Docs**: `http://localhost:8000/docs`
- **Postgres Database**: `localhost:5432`

---

## 5. Judging Track Focus

1. **Security & Compliance (Primary)**: Focuses on autonomous threat signals, credentials exposure, and direct TriggerWare dispatch webhooks when high scores are mapped.
2. **GTM Intelligence**: Monitors competitive hiring spikes (recruitment growth) and strategic executive shifts.
3. **Finance & Market Intelligence**: Highlights SaaS pricing schedule reductions and competitor market pivots.
