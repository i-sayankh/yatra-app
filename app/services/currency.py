import os
import httpx
from dotenv import load_dotenv
from datetime import datetime, timedelta
from services.cache import get_cache, set_cache

load_dotenv()


async def fetch_currency_rates(base_currency: str) -> dict[str, float]:
    """Fetch currency exchange rates from an external API."""
    cache_key = f"currency_{base_currency}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://v6.exchangerate-api.com/v6/{os.getenv('EXCHANGE_RATE_API_KEY')}/latest/{base_currency}"
        )
        response.raise_for_status()
        data = response.json()

        rates = data.get("conversion_rates", {})
        set_cache(cache_key, rates, ttl=3600)  # Cache for 1 hour
        return rates
