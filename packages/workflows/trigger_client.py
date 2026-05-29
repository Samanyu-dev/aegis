import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from apps.backend.config import settings

logger = logging.getLogger("aegis.workflows")

async def trigger_workflow(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fires an automated workflow trigger webhook on TriggerWare.
    Logs execution results locally.
    """
    timestamp = datetime.utcnow().isoformat()
    event_data = {
        "event": event_type,
        "payload": payload,
        "timestamp": timestamp
    }
    
    webhook_raw = settings.TRIGGERWARE_WEBHOOK_URL
    if not webhook_raw or not webhook_raw.strip():
        logger.warning(f"TRIGGERWARE_WEBHOOK_URL not configured. Simulating workflow dispatch for: {event_type}")
        return {
            "status": "success",
            "mode": "simulated",
            "event": event_type,
            "timestamp": timestamp,
            "details": "TriggerWare simulation executed successfully."
        }

    webhook_url = webhook_raw.strip()
    if not webhook_url.startswith("http"):
        webhook_url = f"https://app.triggerware.ai/webhooks/{webhook_url}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_url,
                json=event_data
            )
            if response.status_code in [200, 201, 202]:
                logger.info(f"TriggerWare webhook successfully delivered for {event_type}")
                return {
                    "status": "success",
                    "mode": "live",
                    "event": event_type,
                    "timestamp": timestamp,
                    "status_code": response.status_code
                }
            else:
                logger.error(f"TriggerWare webhook returned status {response.status_code}: {response.text}")
                return {
                    "status": "failed",
                    "mode": "live",
                    "event": event_type,
                    "timestamp": timestamp,
                    "error": f"Status {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Failed to fire TriggerWare workflow webhook: {e}")
        return {
            "status": "failed",
            "mode": "live",
            "event": event_type,
            "timestamp": timestamp,
            "error": str(e)
        }
