import aiohttp
import re
import math
import json
from urllib.parse import urljoin, urlparse

class DiscoveryEngine:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        
        # Secrets regex for JS mining
        self.secret_patterns = {
            'AWS_KEY': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
            'STRIPE_LIVE': re.compile(r'\bsk_live_[0-9a-zA-Z]{24}\b'),
            'GENERIC_API': re.compile(r'api_key\s*[:=]\s*[\"\']([a-zA-Z0-9_\-]{32,})[\"\']')
        }
        
        # "AST" (Regex) patterns for endpoint discovery in JS
        self.endpoint_patterns = [
             re.compile(r'[\"\'](\/api\/v\d+\/[a-zA-Z0-9_\-\/]+)[\"\']'), # "/api/v1/users"
             re.compile(r'const\s+[a-zA-Z0-9_]+\s*=\s*[\"\'](https?:\/\/[^\"\']+)[\"\']'), # const BASE = "http..."
             re.compile(r'\.get\([\"\'](\/[a-zA-Z0-9_\-\/]+)[\"\']') # axios.get('/path')
        ]

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
                {"url": urljoin(target_url, "/product/999"), "tags": ["Zombie Candidate"]},
                {"url": urljoin(target_url, "/users"), "tags": ["Zombie Candidate", "PII Candidate"]},
                {"url": urljoin(target_url, "/api/profile"), "tags": ["Zombie Candidate"]},
                {"url": urljoin(target_url, "/static/app.js"), "tags": ["JS Asset"]}
            ]
        # ------------------------------

        cdx_url = "http://web.archive.org/cdx/search/cdx"
        params = {
            'url': f'*.{domain}/*',
            'output': 'json',
            'fl': 'original,mimetype',
            'collapse': 'urlkey',
            'filter': ['statuscode:200'], 
            'limit': 500
        }
        
        results = []
        try:
             async with self.session.get(cdx_url, params=params, timeout=15) as resp:
                 if resp.status == 200:
                     data = await resp.json()
                     if data and len(data) > 1:
                         # Skip header row
                         for row in data[1:]:
                             url, mimetype = row[0], row[1]
                             # Filter for JSON or potential API endpoints
                             if 'json' in mimetype or '/api/' in url:
                                 results.append({
                                     "url": url,
                                     "tags": ["Zombie Candidate"]
                                 })
        except Exception as e:
            print(f"[!] Wayback mining failed: {e}")
            
        print(f"[*] Wayback mining found {len(results)} potential zombie URLs")
        return results

    def _entropy(self, string):
        """Calculate Shannon entropy of a string"""
        prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

    async def deep_mine_js(self, url, content):
        """
        Protocol B: Deep JS Analysis (Singularity Upgrade)
        1. Source Maps Archeology (Download & Parse)
        2. AST Tracing
        3. Secret Detection
        """
        findings = []
        
        if not content:
            return findings

        # 1. Source Maps
        match = re.search(r'//# sourceMappingURL=(.*)', content)
        if match:
            map_file = match.group(1).strip()
            full_map_url = urljoin(url, map_file)
            
            # Singularity Upgrade: Actually attempt to fetch the map
            print(f"[*] Attempting Source Map Archeology on {full_map_url}...")
            try:
                async with self.session.get(full_map_url) as map_resp:
                    if map_resp.status == 200:
                        map_content = await map_resp.json()
                        sources = map_content.get('sources', [])
                        findings.append({
                            "type": "Source Map Analyzed",
                            "evidence": f"Recovered {len(sources)} source files from map.",
                            "severity": "Low"
                        })
                        
                        # Omniscient Upgrade: Cognitive Source Analysis
                        # Check for vulnerable filenames in the source tree
                        for source_file in sources:
                            if "lodash" in source_file.lower() or "jquery" in source_file.lower():
                                findings.append({
                                    "type": "Vulnerable Dependency (SourceMap)",
                                    "evidence": f"Found legacy library: {source_file}",
                                    "severity": "Medium"
                                })
                            if "config" in source_file.lower() or "secret" in source_file.lower():
                                findings.append({
                                    "type": "Sensitive Source File",
                                    "evidence": f"Potential secret in: {source_file}",
                                    "severity": "Medium"
                                })
                    else:
                        findings.append({
                            "type": "Source Map Detected (Unreachable)",
                            "evidence": full_map_url,
                            "severity": "Low"
                        })
            except Exception as e:
                findings.append({
                     "type": "Source Map Detected (Fetch Failed)",
                     "evidence": f"{full_map_url} ({str(e)})",
                     "severity": "Low"
                })

        # 2. Secret Detection
        for name, pattern in self.secret_patterns.items():
            matches = pattern.findall(content)
            for secret in matches:
                # Entropy check to reduce false positive "sk_live_example"
                if self._entropy(secret) > 3.0: 
                    findings.append({
                        "type": f"Hardcoded Secret ({name})",
                        "evidence": secret[:10] + "...", # Redact for logs
                        "severity": "Critical"
                    })

        # 3. Endpoint Discovery ("AST" Tracing)
        detected_endpoints = set()
        for pattern in self.endpoint_patterns:
            matches = pattern.findall(content)
            for ep in matches:
                # Basic validation
                if len(ep) > 2 and not ep.startswith('//'):
                    full_url = urljoin(url, ep)
                    detected_endpoints.add(full_url)
        
        for ep in detected_endpoints:
             findings.append({
                "type": "Discovered Endpoint",
                "evidence": ep,
                "severity": "Info"
            })

        return findings
