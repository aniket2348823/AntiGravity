import aiohttp
from aiolimiter import AsyncLimiter

class TransportLayer:
    def __init__(self, concurrency=100, rate_limit=20):
        """
        Layer 3: Transport (The Muscle)
        - Uses Token Bucket rate limiter to prevent bans.
        - High concurrency connector.
        """
        self.concurrency = concurrency
        self.rate_limiter = AsyncLimiter(rate_limit, 1) # 20 reqs/sec
        self.session = None

    async def start(self):
        # High-performance setup: AsyncResolver for non-blocking DNS
        connector = aiohttp.TCPConnector(
            limit_per_host=self.concurrency, 
            resolver=aiohttp.AsyncResolver(),
            ssl=False
        )
        self.session = aiohttp.ClientSession(connector=connector)

    async def close(self):
        if self.session:
            await self.session.close()

    async def safe_request(self, method, url, **kwargs):
        """
        Wrapper to respect rate limits and handle errors gracefully.
        """
        if not self.session:
            raise RuntimeError("Transport layer not started")

        async with self.rate_limiter:
            try:
                # Add human-like headers if not present
                if 'headers' not in kwargs:
                    kwargs['headers'] = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                
                async with self.session.request(method, url, **kwargs) as response:
                    # Read content here to release connection back to pool
                    text = await response.text()
                    return {
                        'status': response.status,
                        'text': text,
                        'headers': response.headers,
                        'size': len(text),
                        'latency': 0 # TODO: Measure latency if needed, rough estimate
                    }
            except Exception as e:
                # print(f"Request failed: {url} - {e}")
                return None
