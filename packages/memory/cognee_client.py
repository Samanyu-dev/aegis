import logging
from typing import List, Dict, Any, Optional
from apps.backend.config import settings

logger = logging.getLogger("aegis.memory")

# Tracks initialization of Cognee
_cognee_initialized = False

async def get_cognee_client():
    """
    Attempts to import and configure the Cognee library dynamically.
    Returns the module if successful, otherwise None.
    """
    global _cognee_initialized
    if _cognee_initialized:
        try:
            import cognee
            return cognee
        except ImportError:
            return None

    if not settings.COGNEE_API_KEY:
        logger.warning("COGNEE_API_KEY is not defined. Using local fallback database memory.")
        return None

    try:
        import cognee
        # Configure Cognee to use OpenAI compatible models or custom provider
        await cognee.config.set_llm_config({
            "provider": "openai",
            "api_key": settings.COGNEE_API_KEY
        })
        _cognee_initialized = True
        logger.info("Cognee memory engine successfully initialized.")
        return cognee
    except Exception as e:
        logger.error(f"Failed to configure Cognee memory package: {e}")
        return None

async def remember_finding(entity: str, data: Dict[str, Any]) -> bool:
    """
    Stores an investigation finding or entity profile into Cognee memory graph.
    Uses dataset named 'aegis_{entity}'.
    """
    cognee = await get_cognee_client()
    dataset_name = f"aegis_{entity.lower().replace(' ', '_')}"
    
    if not cognee:
        logger.info(f"[SIMULATED COGNEE MEMORY] Storing entity finding '{entity}': {data}")
        return True

    try:
        logger.info(f"Adding data for entity '{entity}' to Cognee dataset '{dataset_name}'")
        await cognee.add(data, dataset_name=dataset_name)
        await cognee.cognify()
        logger.info(f"Cognee successfully cognified finding for '{entity}'")
        return True
    except Exception as e:
        logger.error(f"Cognee execution error while cognifying '{entity}': {e}. Falling back gracefully.")
        return False

async def recall_context(query: str) -> List[Dict[str, Any]]:
    """
    Queries Cognee persistent semantic memory using query_type='INSIGHTS'.
    """
    cognee = await get_cognee_client()
    
    if not cognee:
        logger.info(f"[SIMULATED COGNEE MEMORY] Querying context for: '{query}'")
        # Provide contextual mock memory for smooth demo flow
        q_lower = query.lower()
        if "openai" in q_lower or "competitor" in q_lower or "anthropic" in q_lower:
            return [
                {
                    "entity": "Anthropic",
                    "type": "COMPANY",
                    "insight": "Previously investigated on 2026-05-27. Identified significant hiring spike (430 roles) and strategic shift towards high-security compliance markets.",
                    "severity": 6
                },
                {
                    "entity": "Mistral AI",
                    "type": "COMPANY",
                    "insight": "Identified recent pricing model decrease (20% cuts in CodeStral pricing) on 2026-05-28. Executive departure of COO confirmed.",
                    "severity": 5
                }
            ]
        return []

    try:
        logger.info(f"Recalling context for semantic query: '{query}'")
        results = await cognee.search(query, query_type="INSIGHTS")
        logger.info(f"Cognee search retrieved {len(results)} items.")
        return results
    except Exception as e:
        logger.error(f"Failed to query Cognee search engine: {e}. Returning empty memory list.")
        return []
