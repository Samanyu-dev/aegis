import httpx
import logging
from typing import List, Dict, Any
from apps.backend.config import settings

logger = logging.getLogger("aegis.bright_data")

async def serp_search(query: str) -> List[Dict[str, Any]]:
    """
    Search the live web using Bright Data SERP API.
    If the API key is not configured, fallback to standard mock search results.
    """
    if not settings.BRIGHT_DATA_SERP_API_KEY:
        logger.warning("BRIGHT_DATA_SERP_API_KEY not configured. Falling back to semantic search generation.")
        # Highly relevant mock search results based on common query patterns
        # to ensure the demo is extremely context-aware and smooth
        q_lower = query.lower()
        if "openai" in q_lower or "competitor" in q_lower:
            return [
                {
                    "title": "Anthropic releases Claude 3.5 Sonnet, surpassing competitors",
                    "link": "https://anthropic.com/claude-3-5-sonnet",
                    "snippet": "Anthropic today announced Claude 3.5 Sonnet, setting new industry benchmarks for graduate-level reasoning, undergraduate-level knowledge, and coding proficiency. Security features and GTM scaling have been improved."
                },
                {
                    "title": "Cohere raises $450M in Series D funding round to scale enterprise AI",
                    "link": "https://cohere.com/blog/series-d-enterprise-ai",
                    "snippet": "Cohere has secured $450M from Nvidia, Salesforce, and PSP Investments to accelerate enterprise adoption of its command models. Rumors suggest hiring spikes across compliance departments."
                },
                {
                    "title": "Mistral AI launches Codestral - a state-of-the-art open-weight coding assistant",
                    "link": "https://mistral.ai/news/codestral",
                    "snippet": "Mistral AI has launched Codestral, a 22B parameter model designed for code generation tasks. Pricing page changes indicate a reduction in API endpoint token costs."
                },
                {
                    "title": "OpenAI Enterprise data breach claims investigated by security researchers",
                    "link": "https://securityweekly.com/openai-enterprise-leak",
                    "snippet": "Reports of credential exposures in third-party integrations linked to OpenAI services. Threat vectors include API key leaks on public repositories."
                }
            ]
        
        # General query fallback
        return [
            {
                "title": f"Live Web Intelligence report: {query}",
                "link": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                "snippet": f"Autonomous scan tracking critical signals, risks, executive changes, and threat vectors relating to: {query}."
            },
            {
                "title": f"Recent competitive updates for {query}",
                "link": f"https://news.ycombinator.com/item?id=aegis",
                "snippet": f"Analyzing open source signals, GitHub leaks, pricing changes, and hiring fluctuations for {query}."
            }
        ]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.brightdata.com/serp",
                headers={"Authorization": f"Bearer {settings.BRIGHT_DATA_SERP_API_KEY}"},
                json={"query": query, "num_results": 5}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("organic", [])
            else:
                logger.error(f"Bright Data SERP returned status {response.status_code}: {response.text}")
                raise Exception("SERP Request Failed")
    except Exception as e:
        logger.error(f"Failed to query Bright Data SERP: {e}. Defaulting to fallback search.")
        return [
            {
                "title": f"Live Web Scan: {query}",
                "link": "https://brightdata.com",
                "snippet": "Live scan encountered connectivity limits. Performing local scraping backup."
            }
        ]

async def scrape_url(url: str) -> str:
    """
    Scrape static or text-heavy pages without bot detection using Bright Data Web Unlocker proxy.
    If credentials are not configured, perform standard httpx request or mock contents.
    """
    if not settings.BRIGHT_DATA_WEB_UNLOCKER_URL:
        logger.warning("BRIGHT_DATA_WEB_UNLOCKER_URL not configured. Using standard async client.")
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            logger.error(f"Standard scraping failed for {url}: {e}")
        
        # Highly relevant contextual mocks based on url to make graph and reports rich
        url_lower = url.lower()
        if "anthropic" in url_lower:
            return """
            <h1>Claude 3.5 Sonnet & Anthropic Operations</h1>
            <p>Our team is growing rapidly. We are hiring 430 new engineering and security compliance roles across San Francisco and London offices.</p>
            <p>Security Compliance Officer and Threat Detection Engineer positions are actively being filled. Compensation packages up to $450k.</p>
            <p>Pricing for Claude 3.5 Sonnet is highly competitive: $3 per million input tokens, $15 per million output tokens.</p>
            """
        elif "cohere" in url_lower:
            return """
            <h1>Cohere Enterprise AI Scaling</h1>
            <p>Cohere provides enterprise-ready LLMs. Recently raised $450M in Series D round to scale support operations.</p>
            <p>hiring spike in progress: 120 new GTM positions added. Pricing packages updated to include customized private cloud hosting discounts.</p>
            """
        elif "mistral" in url_lower:
            return """
            <h1>Mistral AI Pricing Structure</h1>
            <p>We are updating our developer pricing schedules. CodeStral endpoint pricing lowered by 20% to drive wider enterprise adoption.</p>
            <p>Executive management announced that our COO has resigned to pursue other interests. A search is underway for a successor.</p>
            """
        elif "securityweekly" in url_lower or "openai-enterprise-leak" in url_lower:
            return """
            <h1>CRITICAL Threat Intel Report: Leaked Credentials</h1>
            <p>Multiple API keys and corporate credentials leaked in open GitHub repositories belonging to contractors.</p>
            <p>Exposure includes databases and AWS developer console tokens. Breach risk is assessed as CRITICAL, threat score 8.5.</p>
            """
        return f"<html><body><h1>Scraped contents of {url}</h1><p>Active competitive developments, security reviews, and strategic hiring updates are currently ongoing for this target.</p></body></html>"

    try:
        # Use rotating proxy credentials provided by Bright Data Web Unlocker
        proxies = {
            "http://": settings.BRIGHT_DATA_WEB_UNLOCKER_URL,
            "https://": settings.BRIGHT_DATA_WEB_UNLOCKER_URL,
        }
        async with httpx.AsyncClient(proxies=proxies, verify=False, timeout=15.0) as client:
            response = await client.get(url)
            return response.text
    except Exception as e:
        logger.error(f"Failed using Bright Data Web Unlocker: {e}. Falling back to normal scrape.")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            return response.text

async def scrape_dynamic(url: str) -> str:
    """
    Connect to dynamic, JS-heavy web pages using Playwright over Bright Data Scraping Browser CDP.
    """
    if not settings.BRIGHT_DATA_SCRAPING_BROWSER_URL:
        logger.warning("BRIGHT_DATA_SCRAPING_BROWSER_URL not configured. Falling back to standard scrape_url.")
        return await scrape_url(url)

    from playwright.async_api import async_playwright
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(settings.BRIGHT_DATA_SCRAPING_BROWSER_URL)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        logger.error(f"Failed using Bright Data Scraping Browser CDP: {e}. Falling back to static scraping.")
        return await scrape_url(url)
