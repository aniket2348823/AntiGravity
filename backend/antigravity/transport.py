import aiohttp
import time
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
        self.error_count = 0
        self.circuit_open = False,
        self.last_error_time = 0

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

        # Circuit Breaker Check
        if self.circuit_open:
            if time.time() - self.last_error_time > 60:
                self.circuit_open = False
                self.error_count = 0
            else:
                return None # Circuit is open, fast fail

        async with self.rate_limiter:
            try:
                # Add human-like headers if not present
                # Ephemeral Swarm Evasion: Rotate User-Agents
                if 'headers' not in kwargs:
                    import random
                    user_agents = [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
                    ]
                    kwargs['headers'] = {
                        'User-Agent': random.choice(user_agents),
                        'Accept': 'application/json, text/plain, */*'
                    }
                
                async with self.session.request(method, url, **kwargs) as response:
                    # Circuit Breaker Logic
                    if response.status >= 500:
                        self.error_count += 1
                        if self.error_count > 5:
                            self.circuit_open = True
                            self.last_error_time = time.time()
                    else:
                        self.error_count = 0 # Reset on success

                    text = await response.text()
                    return {
                        'status': response.status,
                        'text': text,
                        'headers': response.headers,
                        'size': len(text),
                        'latency': 0 
                    }
            except Exception as e:
                # print(f"Request failed: {url} - {e}")
                return None
