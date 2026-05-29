import logging
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Callable, Optional
from langgraph.graph import StateGraph, END
from packages.shared.bright_data import serp_search, scrape_url, scrape_dynamic
from packages.agents.ai_client import extract_entities, synthesize_intelligence
from packages.memory.cognee_client import remember_finding, recall_context
from packages.workflows.trigger_client import trigger_workflow
from apps.backend.database import AsyncSessionLocal, DBInvestigation, DBSignal, DBWorkflowEvent, DBMemoryNode
from apps.backend.config import settings

logger = logging.getLogger("aegis.graph")

class AegisState(TypedDict):
    target: str
    focus: List[str]
    search_results: List[Dict[str, Any]]
    scraped_content: List[str]
    entities: List[Dict[str, Any]]
    prior_context: str
    risk_score: float
    signals: List[Dict[str, Any]]
    report: Dict[str, Any]
    stream_log: List[str]
    callback: Optional[Callable[[Dict[str, Any]], Any]]  # SSE async callback function

async def scout_node(state: AegisState) -> AegisState:
    """
    Scout Node: Triggers live web search queries.
    Yields search logs.
    """
    target = state["target"]
    focus_str = ", ".join(state["focus"]) if state["focus"] else "general threats"
    message = f"Initiating web reconnaissance for target '{target}' focusing on [{focus_str}]"
    
    logger.info(message)
    state["stream_log"].append(message)
    
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "scout",
            "message": f"Searching live web index for '{target}' intelligence...",
            "timestamp": datetime.utcnow().isoformat()
        })

    # Run multi-query search
    queries = [
        f"{target} competitors security vulnerabilities pricing changes",
        f"{target} credentials exposure database leak",
        f"{target} hiring growth compliance news"
    ]
    
    search_results = []
    for query in queries:
        results = await serp_search(query)
        search_results.extend(results)
        
    state["search_results"] = search_results[:6]  # Cap results
    
    scout_message = f"Web search complete. Found {len(state['search_results'])} organic intelligence references."
    state["stream_log"].append(scout_message)
    
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "scout",
            "message": scout_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    return state

async def investigate_node(state: AegisState) -> AegisState:
    """
    Investigate Node: Deep scrapes top findings, extracts entities, and pulls Cognee context.
    Streams found signals (hiring spike, credentials) dynamically.
    """
    target = state["target"]
    results = state["search_results"]
    
    # Retrieve Cognee Prior Context first
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "investigate",
            "message": f"Retrieving persistent historical context from Cognee Memory graph...",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    prior_mem = await recall_context(target)
    prior_context_str = ""
    if prior_mem:
        prior_context_str = "\n".join([
            f"- Prior Insight on {item.get('entity', 'Target')}: {item.get('insight', '')}"
            for item in prior_mem
        ])
    else:
        prior_context_str = "No prior semantic graph patterns registered in database memory for this target."
        
    state["prior_context"] = prior_context_str
    
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "investigate",
            "message": "Persistent memory retrieved. Commencing deep Web Unlocker scraping...",
            "timestamp": datetime.utcnow().isoformat()
        })

    scraped_content = []
    entities_accumulated = []
    signals_accumulated = []
    
    # Scrape top 3 pages using Web Unlocker
    urls_to_scrape = [res["link"] for res in results[:3] if "link" in res]
    
    for idx, url in enumerate(urls_to_scrape):
        # Showcase Scraping Browser (Playwright CDP) for the primary link if credentials exist!
        if idx == 0 and settings.BRIGHT_DATA_SCRAPING_BROWSER_URL:
            if state["callback"]:
                await state["callback"]({
                    "type": "step",
                    "step": "investigate",
                    "message": f"Connecting to headless scraping browser via Playwright CDP: {url}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            try:
                html = await scrape_dynamic(url)
            except Exception as e:
                logger.error(f"Scraping Browser failed for {url}: {e}. Falling back to Web Unlocker.")
                html = await scrape_url(url)
        else:
            # Use Web Unlocker proxies for subsequent links
            if state["callback"]:
                await state["callback"]({
                    "type": "step",
                    "step": "investigate",
                    "message": f"Scraping proxy host via Web Unlocker: {url}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            html = await scrape_url(url)
            
        scraped_content.append(html[:5000])  # store first 5k characters of content
        
        # Extract entities using Mistral AI/ML API
        extracted = await extract_entities(html)
        
        # Add source URL to signals
        extracted_signals = extracted.get("signals", [])
        for sig in extracted_signals:
            sig["source_url"] = url
            
        entities_accumulated.extend(extracted.get("entities", []))
        signals_accumulated.extend(extracted_signals)
        
        # Stream any signals parsed in real time
        for sig in extracted_signals:
            if state["callback"]:
                await state["callback"]({
                    "type": "signal",
                    "signal": sig["type"],
                    "entity": sig["entity"],
                    "detail": sig["detail"],
                    "severity": sig.get("severity", 5),
                    "timestamp": datetime.utcnow().isoformat()
                })

    state["scraped_content"] = scraped_content
    state["entities"] = entities_accumulated
    state["signals"] = signals_accumulated
    
    investigate_message = f"Deep scraping complete. Extracted {len(entities_accumulated)} entities and captured {len(signals_accumulated)} operational signals."
    state["stream_log"].append(investigate_message)
    
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "investigate",
            "message": investigate_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    return state

async def synthesize_node(state: AegisState) -> AegisState:
    """
    Synthesize Node: Synthesizes threat indexes via GPT-4o, fires TriggerWare webhook,
    cognifies memory elements, and persists database telemetry.
    """
    target = state["target"]
    
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "synthesize",
            "message": "Analyzing threat metrics and competitive shifts via GPT-4o synthesis...",
            "timestamp": datetime.utcnow().isoformat()
        })

    # Assemble raw intelligence findings
    findings = [
        {"entities": state["entities"], "signals": state["signals"]}
    ]
    
    report = await synthesize_intelligence(target, findings, state["prior_context"])
    
    # Persistent Memory: Write entities and results to Cognee Graph
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "synthesize",
            "message": "Writing threat indicators and entity profiles into Cognee Knowledge Graph...",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    for ent in report.get("entities", []):
        await remember_finding(ent["name"], ent)
        
    # TriggerWare Event Check
    triggered_actions = []
    risk_score = report.get("risk_score", 0.0)
    
    if risk_score > 7.0:
        event_type = "HIGH_RISK_DETECTED"
        if state["callback"]:
            await state["callback"]({
                "type": "step",
                "step": "synthesize",
                "message": f"🚨 THREAT BREACH DETECTED (Score {risk_score}/10). Dispatching TriggerWare Automation Webhook...",
                "timestamp": datetime.utcnow().isoformat()
            })
        wf_res = await trigger_workflow(event_type, report)
        triggered_actions.append(event_type)
    
    # Check individual signal triggers
    for sig in report.get("signals", []):
        sig_type = sig.get("type")
        if sig_type in ["BREACH_SIGNAL_FOUND", "EXECUTIVE_CHANGE", "PRICING_CHANGE", "HIRING_SPIKE"]:
            if sig_type not in triggered_actions:
                await trigger_workflow(sig_type, sig)
                triggered_actions.append(sig_type)

    report["workflows_triggered"] = triggered_actions
    state["risk_score"] = risk_score
    state["report"] = report

    # Persist all records into PostgreSQL Database
    if state["callback"]:
        await state["callback"]({
            "type": "step",
            "step": "synthesize",
            "message": "Saving intelligence reports, parsed signals, and timeline nodes into local Database schema...",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    try:
        async with AsyncSessionLocal() as session:
            # 1. Store Investigation
            db_inv = DBInvestigation(
                target=target,
                focus=state["focus"],
                status="complete",
                risk_score=risk_score,
                report=report
            )
            session.add(db_inv)
            await session.flush()  # Extract primary key
            
            # 2. Store Signals
            for sig in report.get("signals", []):
                db_sig = DBSignal(
                    investigation_id=db_inv.id,
                    signal_type=sig["type"],
                    entity=sig["entity"],
                    detail=sig["detail"],
                    severity=sig.get("severity", 5)
                )
                session.add(db_sig)
                
            # 3. Store Memory Nodes (mirrors Cognee for instant UI Force D3 rendering)
            for ent in report.get("entities", []):
                db_node = DBMemoryNode(
                    entity=ent["name"],
                    entity_type=ent["type"],
                    properties={"mentions": ent.get("mentions", 1)}
                )
                session.add(db_node)
                
            # 4. Store TriggerWare Event Logs
            for act in triggered_actions:
                db_wf = DBWorkflowEvent(
                    event_type=act,
                    payload={"target": target, "risk_score": risk_score, "details": f"Automated webhook dispatch for event {act}"}
                )
                session.add(db_wf)
                
            await session.commit()
            logger.info("Successfully persisted investigation run to database.")
    except Exception as e:
        logger.error(f"Failed to persist intelligence results to database: {e}")

    state["stream_log"].append("Report generation finished.")
    return state

# Construct LangGraph State Graph
builder = StateGraph(AegisState)
builder.add_node("scout", scout_node)
builder.add_node("investigate", investigate_node)
builder.add_node("synthesize", synthesize_node)

builder.set_entry_point("scout")
builder.add_edge("scout", "investigate")
builder.add_edge("investigate", "synthesize")
builder.add_edge("synthesize", END)

# Compile Graph
aegis_graph = builder.compile()

async def run_aegis_investigation(target: str, focus: List[str], callback: Optional[Callable[[Dict[str, Any]], Any]] = None) -> Dict[str, Any]:
    """
    Execution wrapper that boots the LangGraph and runs it end-to-end.
    """
    initial_state = AegisState(
        target=target,
        focus=focus,
        search_results=[],
        scraped_content=[],
        entities=[],
        prior_context="",
        risk_score=0.0,
        signals=[],
        report={},
        stream_log=[],
        callback=callback
    )
    
    result = await aegis_graph.ainvoke(initial_state)
    return result.get("report", {})
