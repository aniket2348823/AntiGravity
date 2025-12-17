import aiohttp
import re
from urllib.parse import urljoin, urlparse

class DiscoveryEngine:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_wayback_urls(self, target_url):
        """
        Protocol A: Time Travel Reconnaissance
        Query CDX API for historical endpoints.
        """
        domain = urlparse(target_url).netloc
        print(f"[*] Starting Wayback machine mining for {domain}...")
        
        # --- MOCK FOR LOCAL TESTING ---
        if 'localhost' in domain or '127.0.0.1' in domain:
            print("[*] Localhost detected. Returning mock historical URLs for testing.")
            return [
                urljoin(target_url, "/product/999"), # Soft 404 candidate
                urljoin(target_url, "/users"),       # PII candidate
                urljoin(target_url, "/api/profile"), # Mass Assignment candidate
                urljoin(target_url, "/static/app.js") # JS Source Map candidate
            ]
        # ------------------------------

        cdx_url = "http://web.archive.org/cdx/search/cdx"
        params = {
            'url': f'*.{domain}/*',
            'output': 'json',
            'fl': 'original',
            'collapse': 'urlkey',
            'filter': 'statuscode:200', # ONLY 200 OK
            'limit': 500 # Limit to avoid taking too long for now
        }
        
        found_urls = set()
        try:
             async with self.session.get(cdx_url, params=params, timeout=15) as resp:
                 if resp.status == 200:
                     data = await resp.json()
                     if data and len(data) > 1:
                         # Skip header row
                         for row in data[1:]:
                             found_urls.add(row[0])
        except Exception as e:
            print(f"[!] Wayback mining failed: {e}")
            
        print(f"[*] Wayback mining found {len(found_urls)} unique URLs")
        return list(found_urls)

    async def extract_js_source_map(self, url, content):
        """
        Protocol B: Deep JS Analysis
        Search for source map links in JS files.
        """
        if not url.endswith('.js'):
            return None

        # Look for sourceMappingURL
        # Format: //# sourceMappingURL=file.js.map
        match = re.search(r'//# sourceMappingURL=(.*)', content)
        if match:
            map_file = match.group(1).strip()
            full_map_url = urljoin(url, map_file)
            return full_map_url
        return None
