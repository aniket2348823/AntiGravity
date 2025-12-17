import re
import hashlib

class Soft404Detector:
    def __init__(self):
        self.baseline_hash = 0

    def _simhash(self, text):
        # 1. Tokenize text (break into words)
        tokens = re.findall(r'\w+', text.lower())
        v = [0] * 64
        
        for t in tokens:
            # 2. Hash each token
            h = int(hashlib.md5(t.encode('utf-8')).hexdigest(), 16)
            for i in range(64):
                bit = (h >> i) & 1
                # 3. Add/Subtract weight
                if bit: v[i] += 1
                else:   v[i] -= 1
        
        # 4. Form final fingerprint
        fingerprint = 0
        for i in range(64):
            if v[i] > 0:
                fingerprint |= (1 << i)
        return fingerprint

    def calibrate(self, error_page_content):
        """Learn the signature of a 404 page"""
        if not error_page_content:
            return
        self.baseline_hash = self._simhash(error_page_content)

    def is_soft_404(self, content, threshold=3):
        """Returns True if content is effectively an error page"""
        if self.baseline_hash == 0:
            return False # Not calibrated

        current_hash = self._simhash(content)
        # Calculate Hamming Distance (XOR bits)
        xor_val = self.baseline_hash ^ current_hash
        distance = bin(xor_val).count('1')
        return distance < threshold

class PIIScanner:
    def __init__(self):
        # Pre-compile regex patterns for performance
        self.patterns = {
            'EMAIL': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            # Improved SSN regex to avoid some false positives
            'SSN_US': re.compile(r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b'),
            'PHONE': re.compile(r'\b\+?[1-9]\d{1,14}\b'), # Basic E.164
            'STACK_TRACE': re.compile(r'(Traceback \(most recent call last\)|SQLSTATE|Syntax error|at line \d+)', re.IGNORECASE)
        }
        
        # Allow-list to reduce false positives
        self.ignored_emails = {'support@', 'contact@', 'info@', 'admin@', 'help@', 'noreply@'}

    def scan_content(self, text, url):
        findings = []
        
        # 1. Check for Emails
        emails = self.patterns['EMAIL'].findall(text)
        for email in set(emails): # Deduplicate
            if not any(ignored in email for ignored in self.ignored_emails):
                 # Simple context check - check if it looks like a variable or inside json
                findings.append({
                    "Type": "PII Leak (Email)",
                    "Evidence": email,
                    "Endpoint": url,
                    "Severity": "High"
                })

        # 2. Check for SSNs (High Criticality)
        ssns = self.patterns['SSN_US'].findall(text)
        if ssns:
            findings.append({
                "Type": "PII Leak (SSN)", 
                "Evidence": f"Found {len(ssns)} SSN patterns (Redacted)",
                "Endpoint": url,
                "Severity": "Critical"
            })

        # 3. Check for Debug Traces (Information Disclosure)
        if self.patterns['STACK_TRACE'].search(text):
            findings.append({
                "Type": "Debug Trace Leak",
                "Evidence": "Server stack trace exposed",
                "Endpoint": url,
                "Severity": "Medium"
            })

        return findings

class MassAssignmentDetector:
    def check(self, baseline_resp, fuzzed_resp, endpoint):
        """
        Compare baseline and fuzzed responses to detect deviations.
        baseline_resp/fuzzed_resp: dict with keys {'size', 'latency', 'status'}
        """
        findings = []
        
        size_diff = abs(fuzzed_resp['size'] - baseline_resp['size'])
        size_percent = size_diff / baseline_resp['size'] if baseline_resp['size'] > 0 else 0
        
        # Latency in seconds
        latency_diff = fuzzed_resp['latency'] - baseline_resp['latency'] 
        
        is_suspicious = False
        evidence = {}

        # Ignore static assets for mass assignment
        if endpoint.endswith(('.js', '.css', '.png', '.jpg', '.woff')):
            return []

        if size_percent > 0.05:
            # Only consider size deviation suspicious if it's significant OR accompanied by latency/status change
             is_suspicious = True
             evidence['Size_ Deviation'] = f"{baseline_resp['size']} -> {fuzzed_resp['size']} bytes"
        
        if latency_diff > 0.2: # > 200ms
             is_suspicious = True
             evidence['Latency_Increase'] = f"{latency_diff:.3f}s"

        if fuzzed_resp['status'] != baseline_resp['status']:
            is_suspicious = True
            evidence['Status_Change'] = f"{baseline_resp['status']} -> {fuzzed_resp['status']}"

        if is_suspicious:
            findings.append({
                 "Type": "Mass Assignment Vulnerability",
                 "Endpoint": endpoint,
                 "Risk": "Critical",
                 "Confidence": "High (Differential Analysis)",
                 "Evidence": evidence
            })
            
        return findings
