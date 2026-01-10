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

    def start_scan(self, target_url, scan_mode="Standard"):
        if self.lock.acquire(blocking=False):
            self.scan_log = [] # Reset log
            self.current_findings = [] # Reset findings
            self.current_scan_thread = threading.Thread(target=self._run_scan, args=(target_url.strip(), scan_mode))
            self.current_scan_thread.start()
            return True
        return False

    def _log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry)
        self.scan_log.append(entry)



    def _run_scan(self, target_url, scan_mode):
        scan_id = None
        try:
            self._log(f"Initializing Antigravity Engine for {target_url} [Mode: {scan_mode}]")
            scan_id = db.add_scan(target_url) 
            
            # Callbacks to bridge to existing UI
            def on_log_callback(msg):
                self._log(msg)
                
            def on_finding_callback(finding):
                 self.current_findings.append(finding)

            from antigravity.titan_core import AetherTitanOmniscience

            titan = AetherTitanOmniscience()
            
            # Run async scan synchronously in this thread
            # 1. v5000.0 Singularity Mode (Simulated/Symbolic)
            asyncio.run(titan.commence_singularity(
                target_url, 
                on_log=on_log_callback, 
                on_finding=on_finding_callback,
                scan_mode=scan_mode
            ))
            
            # 2. Classic Orchestrator Mode (Real Network Recon - OPTIONAL if Singularity covers it)
            # Keeping Orchestrator as fallback or parallel if needed, but for "Advanced" demo, Titan is key.
            # Commenting out Orchestrator to avoid double-scanning or confusion unless needed.
            # orchestrator = ScanOrchestrator(...)
            # asyncio.run(orchestrator.run_scan())
            
            # Strict JSON Schema for Reporting
            
            # Strict JSON Schema for Reporting
            final_report = {
                "Scan_Report": {
                    "Target": target_url,
                    "Architecture": "REST / GraphQL", # Placeholder or could be inferred
                    "Vulnerabilities": self.current_findings
                }
            }
            
            db.update_scan_status(scan_id, "Completed", final_report)
            self._log(f"Scan completed. Total findings: {len(self.current_findings)}")
            
        except Exception as e:
            self._log(f"Scan process error: {e}")
            if scan_id:
                 db.update_scan_status(scan_id, "Failed", {"error": str(e)})
        finally:
            self.lock.release()
            self.current_scan_thread = None

scan_manager = ScanManager()
