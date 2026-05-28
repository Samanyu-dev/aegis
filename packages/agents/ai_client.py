import json
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI
from apps.backend.config import settings
from packages.shared.models import IntelligenceReport

logger = logging.getLogger("aegis.ai_client")

def get_openai_client() -> Optional[AsyncOpenAI]:
    """
    Retrieves the AsyncOpenAI client configured for AI/ML API.
    Returns None if no API key is specified.
    """
    if not settings.AIML_API_KEY:
        logger.warning("AIML_API_KEY not configured. Running AI in simulated mode.")
        return None
    
    return AsyncOpenAI(
        api_key=settings.AIML_API_KEY,
        base_url=settings.AIML_API_BASE_URL
    )

async def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extracts entities (companies, persons, vulnerabilities, domains) from scraped content.
    Uses the fast, cheap model 'mistral-7b-instruct'.
    """
    client = get_openai_client()
    
    if not client:
        # High-fidelity mock extraction based on keyword presence
        text_lower = text.lower()
        extracted = {"entities": [], "signals": []}
        
        # Look for Anthropic
        if "anthropic" in text_lower:
            extracted["entities"].append({"name": "Anthropic", "type": "COMPANY", "mentions": 3})
            extracted["entities"].append({"name": "Claude 3.5 Sonnet", "type": "PRODUCT", "mentions": 2})
            if "hiring" in text_lower:
                extracted["signals"].append({
                    "type": "HIRING_SPIKE",
                    "entity": "Anthropic",
                    "detail": "Actively recruiting for 430 engineering, security and compliance roles.",
                    "severity": 6
                })
        
        # Look for Mistral
        if "mistral" in text_lower:
            extracted["entities"].append({"name": "Mistral AI", "type": "COMPANY", "mentions": 4})
            if "coo" in text_lower or "resigned" in text_lower:
                extracted["signals"].append({
                    "type": "EXECUTIVE_CHANGE",
                    "entity": "Mistral AI",
                    "detail": "COO has resigned; strategic search for standard enterprise compliance operations is underway.",
                    "severity": 7
                })
            if "pricing" in text_lower or "cut" in text_lower:
                extracted["signals"].append({
                    "type": "PRICING_CHANGE",
                    "entity": "Mistral AI",
                    "detail": "Developer endpoint pricing reduced by 20% to increase enterprise market share.",
                    "severity": 5
                })

        # Look for leaks
        if "leak" in text_lower or "exposed" in text_lower or "credentials" in text_lower or "breach" in text_lower:
            extracted["entities"].append({"name": "GitHub Repository Leak", "type": "VULNERABILITY", "mentions": 5})
            extracted["signals"].append({
                "type": "BREACH_SIGNAL_FOUND",
                "entity": "GitHub Repository Leak",
                "detail": "Critical exposure of corporate AWS credentials and DB tokens found in contractor public codebases.",
                "severity": 9
            })

        # Add fallback company if nothing is found
        if not extracted["entities"]:
            extracted["entities"].append({"name": "Global Tech Corp", "type": "COMPANY", "mentions": 1})
            
        return extracted

    prompt = f"""
    Analyze the following scraped text and extract key security, competitive, and GTM entities.
    Entities of interest include: COMPANIES, PERSONS, DOMAINS, VULNERABILITIES.
    Signals of interest include: HIRING_SPIKES, BREACH_SIGNALS, EXECUTIVE_CHANGES, PRICING_CHANGES.
    
    Format the output EXACTLY as this JSON object structure:
    {{
        "entities": [
            {{"name": "Entity Name", "type": "COMPANY|PERSON|DOMAIN|VULNERABILITY", "mentions": 3}}
        ],
        "signals": [
            {{"type": "HIRING_SPIKE|BREACH_SIGNAL_FOUND|EXECUTIVE_CHANGE|PRICING_CHANGE", "entity": "Entity Name", "detail": "Detailed descriptions of findings", "severity": 7}}
        ]
    }}
    
    Scraped Text:
    ---
    {text[:5000]}
    ---
    """
    
    try:
        response = await client.chat.completions.create(
            model="mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "You are a threat intelligence and corporate compliance entity extraction engine. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI/ML API entity extraction failed: {e}. Executing local fallback parses.")
        # Graceful fallback logic
        return {"entities": [{"name": "Failed Parse", "type": "COMPANY", "mentions": 1}], "signals": []}

async def synthesize_intelligence(target: str, findings: List[Dict[str, Any]], prior_context: str) -> Dict[str, Any]:
    """
    Synthesizes search findings, extracted signals, and historical Cognee context.
    Produces a complete, structured risk assessment report using 'gpt-4o'.
    """
    client = get_openai_client()
    
    if not client:
        # High-fidelity mock synthesis generator
        logger.info("[SIMULATED AI ROUTER] Generating GPT-4o synthesis report.")
        
        # Assemble standard structured mock report matching IntelligenceReport model
        signals_list = []
        entities_list = []
        
        for f in findings:
            signals_list.extend(f.get("signals", []))
            entities_list.extend(f.get("entities", []))
            
        # De-duplicate entities by summing mentions
        entity_map = {}
        for ent in entities_list:
            name = ent["name"]
            if name not in entity_map:
                entity_map[name] = {"name": name, "type": ent.get("type", "COMPANY"), "mentions": 0}
            entity_map[name]["mentions"] += ent.get("mentions", 1)
            
        final_entities = list(entity_map.values())
        
        # Assess risk score based on signal severity
        max_severity = 0.0
        if signals_list:
            max_severity = max(float(sig.get("severity", 5.0)) for sig in signals_list)
        else:
            max_severity = 4.2
            
        # Give risk levels based on scores
        risk_score = min(max_severity + 0.5, 10.0)
        if risk_score >= 8.0:
            risk_level = "CRITICAL"
        elif risk_score >= 6.0:
            risk_level = "HIGH"
        elif risk_score >= 4.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        return {
            "target": target,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "executive_summary": f"Autonomous intelligence scan completed for {target}. We monitored public channels, corporate documentation, and threat databases. Prior memory suggests related patterns in competitive tech space. Identified {len(signals_list)} significant live web signals, including potential executive shifts and pricing policy fluctuations among top market players.",
            "signals": signals_list,
            "entities": final_entities,
            "sources": [
                {"title": f"Live Analysis of {target} trends", "url": f"https://www.google.com/search?q={target}", "snippet": "Aggregated news updates and search index benchmarks."},
                {"title": "Open Source Threat Intelligence feeds", "url": "https://github.com", "snippet": "Scanned public contractor codebases and developer API configurations."}
            ],
            "recommendations": [
                "Deploy proactive vulnerability scanning on all public contractor code repos.",
                "Review strategic competitive enterprise discount pricing schemas to maintain GTM margins.",
                "Initiate direct stakeholder inquiries regarding executive GTM resource reallocations."
            ],
            "prior_context": prior_context or "No prior historical analysis was recorded in Cognee database for this entity.",
            "workflows_triggered": ["HIGH_RISK_DETECTED" if risk_score > 7 else "ROUTINE_MONITORING"],
            "generated_at": datetime.utcnow().isoformat()
        }

    prompt = f"""
    You are AEGIS, the Autonomous Enterprise Intelligence Operating System.
    You are performing a synthesis and threat assessment on target '{target}'.
    
    Here are the raw investigative findings collected from Bright Data web search and Unlocker scraper:
    {json.dumps(findings, indent=2)}
    
    Here is the historical context retrieved from Cognee memory:
    {prior_context}
    
    Generate a full structured intelligence report. The report must contain a threat score from 0.0 to 10.0, risk level assessment, a high-level executive summary, deduplicated entities, signals, sources, and professional security/GTM recommendations.
    
    Format the response output strictly as a JSON object matching this schema:
    {{
        "target": "{target}",
        "risk_score": 7.5,
        "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
        "executive_summary": "Thorough professional analysis detailing the threats and GTM indicators...",
        "signals": [
            {{"type": "HIRING_SPIKE|BREACH_SIGNAL_FOUND|EXECUTIVE_CHANGE|PRICING_CHANGE", "entity": "Entity Name", "detail": "Detailed text", "severity": 8, "source_url": "url"}}
        ],
        "entities": [
            {{"name": "Entity Name", "type": "COMPANY|PERSON|DOMAIN|VULNERABILITY", "mentions": 4}}
        ],
        "sources": [
            {{"title": "Source title", "url": "url", "snippet": "brief snippet"}}
        ],
        "recommendations": [
            "Actionable professional recommendation 1",
            "Actionable professional recommendation 2"
        ]
    }}
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional executive GTM and cybersecurity risk assessor. Respond only in raw JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI/ML API GPT-4o report synthesis failed: {e}. Defaulting to structured local parser.")
        return {
            "target": target,
            "risk_score": 5.0,
            "risk_level": "MEDIUM",
            "executive_summary": "System encountered processing limitations during GPT-4o synthesis. Generated a default telemetry report.",
            "signals": [],
            "entities": [],
            "sources": [],
            "recommendations": ["Re-run AEGIS scan."],
            "prior_context": prior_context,
            "workflows_triggered": [],
            "generated_at": datetime.utcnow().isoformat()
        }
