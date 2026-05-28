import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from apps.backend.config import settings
from apps.backend.database import (
    init_db, get_db, DBInvestigation, DBSignal, DBWorkflowEvent, DBMemoryNode
)
from packages.agents.graph import run_aegis_investigation
from packages.shared.models import InvestigationRequest

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aegis.backend")

app = FastAPI(
    title="AEGIS — Autonomous Enterprise Intelligence Operating System Backend",
    version="1.0.0",
    description="Live web scanning, LangGraph agents orchestration, Cognee memory graphs, and TriggerWare alert dispatches."
)

# Enable CORS for Next.js dev server and production URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Auto-initializes the PostgreSQL/SQLite database tables on launch.
    """
    logger.info("Initializing AEGIS backend service...")
    await init_db()
    logger.info("Backend service successfully online.")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }

@app.get("/api/investigate")
async def investigate_get(
    target: str = Query(..., description="Target entity/topic to scan"),
    focus: str = Query("", description="Comma-separated focus categories"),
    request: Request = None
):
    """
    GET investigation endpoint returning standard Server-Sent Events (SSE).
    Perfect match for standard frontend EventSource connections.
    """
    focus_list = [f.strip() for f in focus.split(",") if f.strip()]
    return await handle_investigation_stream(target, focus_list)

@app.post("/api/investigate")
async def investigate_post(payload: InvestigationRequest):
    """
    POST investigation endpoint returning Server-Sent Events.
    """
    return await handle_investigation_stream(payload.target, payload.focus)

async def handle_investigation_stream(target: str, focus: List[str]):
    """
    Orchestrates the background LangGraph execution and feeds progress to the SSE stream.
    """
    queue = asyncio.Queue()
    
    async def sse_callback(event: Dict[str, Any]):
        await queue.put(event)
        
    async def run_agents_workflow():
        try:
            logger.info(f"Triggering background LangGraph orchestration for '{target}'...")
            report = await run_aegis_investigation(target, focus, sse_callback)
            # Push completed report to queue
            await queue.put({"type": "complete", "report": report})
        except Exception as e:
            logger.error(f"Error in LangGraph investigation: {e}", exc_info=True)
            await queue.put({"type": "step", "step": "error", "message": f"Critical engine failure: {str(e)}", "timestamp": datetime.utcnow().isoformat()})
            await queue.put({"type": "complete", "report": {
                "target": target,
                "risk_score": 0.0,
                "risk_level": "LOW",
                "executive_summary": f"Scan failed to complete due to processing errors: {str(e)}",
                "signals": [],
                "entities": [],
                "sources": [],
                "recommendations": ["Re-run AEGIS scan."],
                "prior_context": "Failed to load prior context.",
                "workflows_triggered": []
            }})
        finally:
            # Signal the end of generator stream
            await queue.put(None)
            
    # Deploy background task
    asyncio.create_task(run_agents_workflow())
    
    async def sse_generator():
        while True:
            event = await queue.get()
            if event is None:
                break
            # Standard SSE packet payload
            yield {
                "event": "message",
                "data": json.dumps(event)
            }
            
    return EventSourceResponse(sse_generator())

@app.get("/api/memory/{entity}")
async def get_entity_memory(entity: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves semantic nodes, relationship links, and alert timeline
    associated with an entity for interactive D3 graph rendering.
    """
    try:
        # 1. Fetch all memory nodes from DB
        stmt = select(DBMemoryNode).order_by(desc(DBMemoryNode.updated_at))
        res = await db.execute(stmt)
        all_nodes = res.scalars().all()
        
        # 2. Build D3 Nodes & Edges structure
        nodes = []
        edges = []
        entity_names = set()
        
        # Add target entity as primary node
        nodes.append({
            "id": entity,
            "label": entity,
            "type": "COMPANY",
            "val": 15
        })
        entity_names.add(entity.lower())
        
        # Add other entities and draw edges connecting to primary/competitor
        for n in all_nodes:
            name_lower = n.entity.lower()
            if name_lower not in entity_names:
                entity_names.add(name_lower)
                # Assign visual weight based on entity mentions
                props = n.properties or {}
                mentions = props.get("mentions", 1)
                nodes.append({
                    "id": n.entity,
                    "label": n.entity,
                    "type": n.entity_type,
                    "val": 5 + min(mentions * 2, 10)
                })
                # Add default edge to target center
                edges.append({
                    "source": entity,
                    "target": n.entity,
                    "label": "associated"
                })

        # 3. Retrieve signals associated to construct Timeline
        sig_stmt = select(DBSignal).order_by(desc(DBSignal.created_at)).limit(15)
        sig_res = await db.execute(sig_stmt)
        signals = sig_res.scalars().all()
        
        timeline = [
            {
                "id": s.id,
                "event": s.signal_type,
                "detail": s.detail,
                "severity": s.severity,
                "timestamp": s.created_at.isoformat()
            }
            for s in signals
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "timeline": timeline
        }
    except Exception as e:
        logger.error(f"Error fetching memory structure for {entity}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/investigations")
async def list_investigations(db: AsyncSession = Depends(get_db)):
    """
    Returns historical intelligence reports.
    """
    try:
        stmt = select(DBInvestigation).order_by(desc(DBInvestigation.created_at)).limit(20)
        res = await db.execute(stmt)
        invs = res.scalars().all()
        return [
            {
                "id": i.id,
                "target": i.target,
                "focus": i.focus,
                "status": i.status,
                "risk_score": i.risk_score,
                "report": i.report,
                "created_at": i.created_at.isoformat()
            }
            for i in invs
        ]
    except Exception as e:
        logger.error(f"Failed listing investigations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows")
async def list_workflow_events(db: AsyncSession = Depends(get_db)):
    """
    Returns triggered TriggerWare workflow pipelines log.
    """
    try:
        stmt = select(DBWorkflowEvent).order_by(desc(DBWorkflowEvent.triggered_at)).limit(20)
        res = await db.execute(stmt)
        wfs = res.scalars().all()
        return [
            {
                "id": w.id,
                "event_type": w.event_type,
                "payload": w.payload,
                "triggered_at": w.triggered_at.isoformat()
            }
            for w in wfs
        ]
    except Exception as e:
        logger.error(f"Failed listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report/{investigation_id}/export")
async def export_report(investigation_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns high-grade Markdown format report of investigation details.
    """
    try:
        stmt = select(DBInvestigation).where(DBInvestigation.id == investigation_id)
        res = await db.execute(stmt)
        inv = res.scalars().first()
        
        if not inv:
            raise HTTPException(status_code=404, detail="Investigation record not found.")
            
        report_data = inv.report or {}
        
        # Format Report markdown
        md = f"""# AEGIS INTEL REPORT — {report_data.get('target', inv.target).upper()}
Generated at: {report_data.get('generated_at', inv.created_at.isoformat())}
Risk score: {report_data.get('risk_score', inv.risk_score)} / 10.0 ({report_data.get('risk_level', 'MEDIUM')})

---

## Executive Summary
{report_data.get('executive_summary', 'No summary details compiled.')}

## Threat Signals Detected
"""
        for sig in report_data.get("signals", []):
            md += f"- **[{sig.get('type')}]** (Severity: {sig.get('severity')}/10) in {sig.get('entity')}: {sig.get('detail')} [Source]({sig.get('source_url')})\n"
            
        md += "\n## Core Entities Extracted\n"
        for ent in report_data.get("entities", []):
            md += f"- **{ent.get('name')}** ({ent.get('type')} — Mentions: {ent.get('mentions')})\n"
            
        md += "\n## Actionable Recommendations\n"
        for rec in report_data.get("recommendations", []):
            md += f"1. {rec}\n"
            
        md += f"\n## Cognee Persistent Memory Context\n{report_data.get('prior_context', 'No memory matched.')}\n"
        
        return {
            "id": investigation_id,
            "filename": f"aegis_report_{inv.target.lower().replace(' ', '_')}.md",
            "markdown": md
        }
    except Exception as e:
        logger.error(f"Failed exporting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
