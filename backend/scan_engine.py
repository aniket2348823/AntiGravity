import threading
import time
import db
import requests
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from antigravity import ScanOrchestrator
import asyncio

class ScanManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_scan_thread = None
        self.scan_log = []
        self.current_findings = []

    def is_scanning(self):
        return self.lock.locked()

    def get_realtime_data(self):
        """Returns current log and findings for real-time UI updates"""
        return {
            "log": self.scan_log[-50:], # Return last 50 logs
            "findings": self.current_findings
        }

    def start_scan(self, target_url):
        if self.lock.acquire(blocking=False):
            self.scan_log = [] # Reset log
            self.current_findings = [] # Reset findings
            self.current_scan_thread = threading.Thread(target=self._run_scan, args=(target_url.strip(),))
            self.current_scan_thread.start()
            return True
        return False

    def _log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry)
        self.scan_log.append(entry)

    def _crawl(self, start_url, max_depth=2):
        self._log(f"Starting crawler on {start_url} (Depth: {max_depth})")
        visited = set()
        queue = [(start_url, 0)]
        found_links = set()
        
        domain = urlparse(start_url).netloc

        while queue:
            url, depth = queue.pop(0)
            if url in visited or depth > max_depth:
                continue
            visited.add(url)
            found_links.add(url)

            try:
                self._log(f"Crawling: {url}")
                res = requests.get(url, timeout=5, verify=False)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(url, href)
                        # Only crawl internal links
                        if urlparse(full_url).netloc == domain:
                            if full_url not in visited:
                                queue.append((full_url, depth + 1))
            except Exception as e:
                self._log(f"Failed to crawl {url}: {e}")
        
        return list(found_links)

    def _run_scan(self, target_url):
        scan_id = None
        try:
            self._log(f"Initializing Antigravity Engine for {target_url}")
            scan_id = db.add_scan(target_url) 
            
            # Callbacks to bridge to existing UI
            def on_log_callback(msg):
                self._log(msg)
                
            def on_finding_callback(finding):
                 self.current_findings.append(finding)

            orchestrator = ScanOrchestrator(
                target_url, 
                on_log=on_log_callback, 
                on_finding=on_finding_callback
            )
            
            # Run async scan synchronously in this thread
            # Since this is a dedicated thread, we can use asyncio.run()
            results = asyncio.run(orchestrator.run_scan())
            
            db.update_scan_status(scan_id, "Completed", {
                "vulnerabilities": self.current_findings,
                "target": target_url
            })
            self._log(f"Scan completed. Total findings: {len(self.current_findings)}")
            
        except Exception as e:
            self._log(f"Scan process error: {e}")
            if scan_id:
                 db.update_scan_status(scan_id, "Failed", {"error": str(e)})
        finally:
            self.lock.release()
            self.current_scan_thread = None

scan_manager = ScanManager()
