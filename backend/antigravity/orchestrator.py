import asyncio
import time
import uuid
from urllib.parse import urlparse, urljoin
from .transport import TransportLayer
from .discovery import DiscoveryEngine
from .analysis import Soft404Detector, PIIScanner, MassAssignmentDetector

class ScanOrchestrator:
    def __init__(self, target_url, on_log=None, on_finding=None):
        self.target = target_url
        self.domain = urlparse(target_url).netloc
        self.transport = TransportLayer()
        self.discovery = None 
        self.soft404 = Soft404Detector()
        self.pii_scanner = PIIScanner()
        self.mass_assignment = MassAssignmentDetector()
        
        self.queue = asyncio.Queue()
        self.visited = set()
        self.findings = []
        self.logs = []
        self.running = False
        
        self.on_log = on_log
        self.on_finding = on_finding

    def log(self, msg):
        # timestamp = time.strftime("%H:%M:%S")
        # print(f"[{timestamp}] {msg}")
        self.logs.append(msg)
        if self.on_log:
            self.on_log(msg)

    def _add_finding(self, finding):
        self.findings.append(finding)
        if self.on_finding:
            self.on_finding(finding)

    async def run_scan(self):
        self.running = True
        self.log(f"Starting Antigravity Scan on {self.target}")
        await self.transport.start()
        self.discovery = DiscoveryEngine(self.transport.session)
        
        try:
            # 1. Calibrate Soft 404
            self.log("Calibrating Soft 404 Protocol...")
            random_guid = str(uuid.uuid4())
            error_url = urljoin(self.target, f"/api/v1/{random_guid}")
            
            resp = await self.transport.safe_request('GET', error_url)
            if resp and resp['status'] == 200:
                self.soft404.calibrate(resp['text'])
                self.log(f"Soft 404 Baseline established with hash: {bin(self.soft404.baseline_hash)}")
            else:
                 self.log(f"Soft 404 Calibration note: Error 404 behavior is standard (Status: {resp['status'] if resp else 'None'}).")

            # 2. Add Target to Queue
            await self.queue.put(self.target)
            
            # 3. Wayback Mining (Protocol A)
            self.log("Executing 'Time Travel' Reconnaissance...")
            wayback_urls = await self.discovery.fetch_wayback_urls(self.target)
            self.log(f"Found {len(wayback_urls)} historical endpoints.")
            for url in wayback_urls:
                if url not in self.visited:
                    await self.queue.put(url)
            
            # 4. Start Workers
            num_workers = 10
            workers = [asyncio.create_task(self.worker(f"Worker-{i}")) for i in range(num_workers)]
            
            # Wait for queue to process
            await self.queue.join()
            
            # Cancel workers
            for w in workers:
                w.cancel()
                
        except Exception as e:
            self.log(f"Critical Scan Error: {e}")
        finally:
            await self.transport.close()
            self.running = False
            self.log("Scan Completed.")
            
        return {
            "target": self.target,
            "findings": self.findings,
            "logs": self.logs
        }

    async def worker(self, name):
        while True:
            try:
                url = await self.queue.get()
                if url in self.visited:
                    self.queue.task_done()
                    continue
                
                self.visited.add(url)
                
                # Check domain scope
                if urlparse(url).netloc != self.domain:
                    self.queue.task_done()
                    continue

                # self.log(f"[{name}] Scanning {url}...")
                
                # Basic Fetch
                t0 = time.time()
                resp = await self.transport.safe_request('GET', url)
                latency = time.time() - t0
                
                if not resp:
                    self.queue.task_done()
                    continue

                resp['latency'] = latency
                
                # Protocol C: Signal Processing (Soft 404)
                if resp['status'] == 200:
                    if self.soft404.is_soft_404(resp['text']):
                        self.log(f"[{name}] Discarded Soft 404: {url}")
                    else:
                        self.log(f"[{name}] VALID API FOUND: {url}")
                        
                        # Protocol D.2: PII scan
                        pii_hits = self.pii_scanner.scan_content(resp['text'], url)
                        if pii_hits:
                            self.log(f"[{name}] CRITICAL: PII Detected on {url}")
                            # Map to old format for compatibility if needed, but keeping new properties for now
                            for hit in pii_hits:
                                self._add_finding({
                                    "name": hit['Type'],
                                    "severity": hit['Severity'],
                                    "description": f"Evidence: {hit['Evidence'][:100]}...",
                                    "url": url,
                                    "full_evidence": hit
                                })
                            
                        # Protocol D.1: Mass Assignment (Param Miner)
                        # Construct fuzz URL
                        separator = '&' if '?' in url else '?'
                        fuzz_url = f"{url}{separator}admin=true&debug=1&test=true"
                            
                        t1 = time.time()
                        fuzz_resp = await self.transport.safe_request('GET', fuzz_url)
                        fuzz_latency = time.time() - t1
                        
                        if fuzz_resp:
                             fuzz_resp['latency'] = fuzz_latency
                             # Only check Mass Assignment if original was 200 and kept structure
                             ma_hits = self.mass_assignment.check(resp, fuzz_resp, url)
                             if ma_hits:
                                 self.log(f"[{name}] HIGH: Mass Assignment Detected on {url}")
                                 for hit in ma_hits:
                                      self._add_finding({
                                        "name": hit['Type'],
                                        "severity": hit['Risk'], # Mapping 'Risk' to 'severity'
                                        "description": "Response deviation detected (Size/Latency/Status)",
                                        "url": url,
                                        "full_evidence": hit
                                    })
                        
                        # Protocol B: Deep JS Analysis
                        # If it is a JS file or has JS content
                        map_url = await self.discovery.extract_js_source_map(url, resp['text'])
                        if map_url:
                            self.log(f"[{name}] Source Map Found: {map_url}")
                            self._add_finding({
                                "name": "Source Map Detected",
                                "severity": "Low",
                                "description": f"Source map exposed at {map_url}",
                                "url": url
                            })
                            # TODO: Protocol B.1 download map file

            except Exception as e:
                # self.log(f"Worker Error: {e}")
                pass
            finally:
                self.queue.task_done()
