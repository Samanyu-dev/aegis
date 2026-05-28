# AEGIS — System Architecture Specification

AEGIS is an AI-Native Autonomous Enterprise Intelligence Operating System designed to scan public news, codebases, threat records, and business directories in real time, extract competitive and security intelligence, retain findings in a semantic graph, and trigger action pipelines dynamically.

---

## High-Level Architecture Flow

```
                      +-------------------+
                      |   Next.js Front   | <----------+
                      |  (Command Dashboard)|           |
                      +-------------------+           | SSE (Server-Sent Events)
                                |                     |
                                v                     |
                      +-------------------+           |
                      |   FastAPI Server  | ----------+
                      +-------------------+
                        |               |
                        | (LangGraph)   +-----------------------+
                        v                                       v
             +---------------------+                 +--------------------+
             |  Multi-Agent Engine |                 | PostgreSQL Schema  |
             +---------------------+                 | - investigations   |
               |        |        |                   | - signals          |
               |        |        |                   | - workflow_events  |
               v        v        v                   | - memory_nodes     |
             Scout Investig. Synthesize              +--------------------+
```

---

## 1. Multi-Agent Engine (LangGraph Lifecycle)

AEGIS implements a 3-Node StateGraph (`AegisState`):

### 1.1 SCOUT NODE (Live Web Reconnaissance)
- **Role**: Coordinates deep searches on target entities.
- **Operations**: Runs 3-5 customized, semantic queries concurrently via **Bright Data SERP API** to discover public news articles, security leaks, job postings, and pricing updates.
- **Telemetry**: Emits incremental SSE events `{"step": "scout", "message": "Searching..."}`.

### 1.2 INVESTIGATE NODE (Deep Page Scraping & Extraction)
- **Role**: Scrapes pages and extracts raw indicators.
- **Operations**:
  1. Grabs top URLs and scrapes content using **Bright Data Web Unlocker** (rotating proxy channels) or **Scraping Browser** (CDP headless protocol for JS-heavy web interfaces).
  2. Queries **AI/ML API** (executing on cost-effective `mistral-7b-instruct`) to extract standard entity objects (PERSON, COMPANY, DOMAIN, VULNERABILITY) and threat signals.
  3. Queries **Cognee Semantic Graph** to retrieve historical context of previously mapped entities.
- **Telemetry**: Emits real-time parsed threat signals like `{"type": "signal", "signal": "HIRING_SPIKE"}`.

### 1.3 SYNTHESIZE NODE (Intelligence Assessment & Action dispatches)
- **Role**: High-level reasoning, report assembly, and automation triggers.
- **Operations**:
  1. Feeds the entire telemetry log (scraped snippets, extracted indicators, prior memories) to **AI/ML API** (routing to strong `gpt-4o`) to compile a standardized JSON `IntelligenceReport`.
  2. Index all entity records into **Cognee Memory Database** to establish relationships for future scans.
  3. Evaluates overall threat metrics. If the threat score exceeds `7.0/10.0`, dispatches the `HIGH_RISK_DETECTED` webhook to **TriggerWare** to alert the security operations center.
  4. Saves the results to our local PostgreSQL schemas.
- **Telemetry**: Emits completed SSE payload `{"type": "complete", "report": {...}}`.

---

## 2. Dynamic Partner Integrations Spec

### 2.1 Bright Data (SERP, Web Unlocker & Scraping Browser)
- **SERP API**: Used for targeted, multi-query searches to parse dynamic indexed links.
- **Web Unlocker**: Used to scrape static pages like company about, blog post, or pricing tables without triggering Cloudflare/bot barriers.
- **Scraping Browser**: Leveraged via Playwright's connect protocol for dynamic client-side JS websites.

### 2.2 Cognee (Persistent Memory Graph)
- Retains corporate data profiles across multiple disjoint investigation runs. Before every research cycle, Cognee is queried for prior facts. After every run, Cognee updates the knowledge graph, giving the agent persistent "memory" of past findings.

### 2.3 TriggerWare (Workflow Automation)
- Translates AI findings into automatic operations. When AEGIS uncovers severe security metrics (credentials leaks) or strategic GTM events (hiring spikes, massive pricing cuts), it dispatches webhooks to TriggerWare pipelines to fire email warnings, database updates, or corporate alerts.

### 2.4 AI/ML API (Multi-Model Smart Routing)
- Rather than a one-size-fits-all LLM choice, AEGIS routes instructions based on complexity:
  - **Mistral-7b-instruct**: Fast, low-latency JSON structured extraction.
  - **GPT-4o**: Highly-reasoned executive report synthesis, scoring, and recommendation layouts.
