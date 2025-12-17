import threading
import time
import db
import requests
import json
from urllib.parse import urljoin

class ScanManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_scan_thread = None

    def is_scanning(self):
        return self.lock.locked()

    def start_scan(self, target_url):
        if self.lock.acquire(blocking=False):
            self.current_scan_thread = threading.Thread(target=self._run_scan, args=(target_url.strip(),))
            self.current_scan_thread.start()
            return True
        return False

    def _run_scan(self, target_url):
        scan_id = None
        try:
            scan_id = db.add_scan(target_url) 
            print(f"Starting scan {scan_id} on {target_url}")
            findings = []
            
            # Helper for robust requests
            def safe_get(url, timeout=10):
                try:
                    return requests.get(url, timeout=timeout, verify=False), None
                except requests.RequestException as e:
                    return None, str(e)
            
            # 1. Connectivity Check & Header Analysis
            res, error = safe_get(target_url)
            if error:
                # If connection failed, we can't do much more. Report critical error.
                findings.append({
                    "name": "Connection Failed",
                    "severity": "Critical",
                    "description": f"Could not connect to target: {error}"
                })
            else:
                # Headers
                headers = res.headers
                required_headers = {
                    'Content-Security-Policy': 'High',
                    'Strict-Transport-Security': 'High',
                    'X-Frame-Options': 'Medium',
                    'X-Content-Type-Options': 'Medium'
                }
                for header, severity in required_headers.items():
                    if header not in headers:
                        findings.append({
                            "name": f"Missing Header: {header}",
                            "severity": severity,
                            "description": f"The {header} security header is missing."
                        })
                if 'Server' in headers:
                    findings.append({
                        "name": f"Server Info Leak",
                        "severity": "Low",
                        "description": f"Server header exposed: {headers['Server']}"
                    })

                # 2. Method Analysis
                methods = ['OPTIONS', 'PUT', 'DELETE', 'TRACE']
                for method in methods:
                    try:
                        m_res = requests.request(method, target_url, timeout=5, verify=False)
                        if m_res.status_code < 405 and m_res.status_code != 404:
                            findings.append({
                                "name": f"Unsafe Method Enabled: {method}",
                                "severity": "Medium",
                                "description": f"Method {method} returned status {m_res.status_code}"
                            })
                    except: pass

                # 3. Directory Enumeration
                path_severity = {
                    '/.env': 'Critical',
                    '/.git': 'Critical',
                    '/backup': 'High',
                    '/config': 'High',
                    '/admin': 'Medium',
                    '/robots.txt': 'Low'
                }
                
                for path, severity in path_severity.items():
                    full_url = urljoin(target_url, path)
                    d_res, _ = safe_get(full_url, timeout=5)
                    if d_res and d_res.status_code == 200:
                        findings.append({
                            "name": f"Sensitive File Found: {path}",
                            "severity": severity,
                            "description": f"Accessible file or directory found at {path}. Risk level depends on content."
                        })

                # 4. Basic XSS Check (Reflected)
                xss_payload = "<script>alert('XSS')</script>"
                # Try appending to URL query
                xss_url = f"{target_url}?q={xss_payload}"
                x_res, _ = safe_get(xss_url, timeout=5)
                if x_res and xss_payload in x_res.text:
                    findings.append({
                        "name": "Reflected XSS Vulnerability",
                        "severity": "High",
                        "description": "The application reflects user input without sanitization (Basic Test)."
                    })

                # 5. Basic SQL Injection Check
                sqli_payload = "' OR '1'='1"
                sqli_url = f"{target_url}?id={sqli_payload}"
                s_res, _ = safe_get(sqli_url, timeout=5)
                if s_res and ("syntax error" in s_res.text.lower() or "sql" in s_res.text.lower()):
                     findings.append({
                        "name": "Potential SQL Injection",
                        "severity": "High",
                        "description": "Database error messages detected in response to SQL payload."
                    })


            results = {
                "vulnerabilities": findings,
                "target": target_url
            }
            
            db.update_scan_status(scan_id, "Completed", results)
            print(f"Scan {scan_id} completed with {len(findings)} findings.")
            
        except Exception as e:
            print(f"Scan failed: {e}")
            if scan_id:
                 db.update_scan_status(scan_id, "Failed", {"error": str(e)})
        finally:
            self.lock.release()
            self.current_scan_thread = None

scan_manager = ScanManager()
