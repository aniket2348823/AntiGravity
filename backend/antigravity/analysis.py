import re
import hashlib

class BayesianClassifier:
    def __init__(self):
        # Mocked Naive Bayes for WAF detection vs Soft 404
        # In a real system, this would load a trained model or use scikit-learn
        self.waf_keywords = {
            'blocked', 'forbidden', 'waf', 'firewall', 'security', 'attack', 
            'malicious', 'denied', 'captcha', 'challenge'
        }
        self.error_keywords = {
            'not found', '404', 'missing', 'moved', 'doesn\'t exist', 'oops'
        }

    def classify(self, text):
        text_lower = text.lower()
        waf_score = 0
        error_score = 0

        tokens = re.findall(r'\w+', text_lower)
        for t in tokens:
            if t in self.waf_keywords:
                waf_score += 1
            if t in self.error_keywords:
                error_score += 1
        
        # Simple probability logic
        if waf_score > 0 and waf_score > error_score:
            return "WAF_BLOCK"
        elif error_score > 0:
            return "GENERIC_ERROR"
        else:
            return "GENERIC_SUCCESS"

class Soft404Detector:
    def __init__(self):
        self.baseline_hash = 0
        self.baseline_tokens = set()

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

    def _get_tokens(self, text):
        return set(re.findall(r'\w+', text.lower()))

    def calibrate(self, error_page_content):
        """Learn the signature of a 404 page"""
        if not error_page_content:
            return
        self.baseline_hash = self._simhash(error_page_content)
        self.baseline_tokens = self._get_tokens(error_page_content)

    def is_soft_404(self, content, threshold=3, jaccard_threshold=0.85):
        """Returns True if content is effectively an error page"""
        if self.baseline_hash == 0:
            return False # Not calibrated

        # 1. SimHash Hamming Distance
        current_hash = self._simhash(content)
        xor_val = self.baseline_hash ^ current_hash
        distance = bin(xor_val).count('1')
        
        if distance < threshold:
            return True

        # 2. Jaccard Similarity
        current_tokens = self._get_tokens(content)
        if not current_tokens or not self.baseline_tokens:
             return False
             
        intersection = len(self.baseline_tokens.intersection(current_tokens))
        union = len(self.baseline_tokens.union(current_tokens))
        jaccard_index = intersection / union if union > 0 else 0
        
        return jaccard_index > jaccard_threshold

class PIIScanner:
    def __init__(self):
        # Pre-compile regex patterns for performance
        self.patterns = {
            'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            # Strict SSN: 000-00-0000 (US)
            'SSN_US': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'STACK_TRACE': re.compile(r'(Traceback \(most recent call last\)|SQLSTATE|Syntax error|at line \d+)', re.IGNORECASE)
        }
        
        # Strict exclusion list
        self.ignored_emails = {'support@', 'contact@', 'info@', 'admin@', 'help@', 'noreply@', 'test@', 'example.com'}

    def scan_content(self, text, url):
        findings = []
        
        # 1. Check for Emails
        emails = self.patterns['EMAIL'].findall(text)
        for email in set(emails): # Deduplicate
            if not any(ignored in email.lower() for ignored in self.ignored_emails):
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

class SQLInjectionDetector:
    def __init__(self):
        self.error_patterns = [
            re.compile(r"(SQL syntax.*MySQL|Warning.*mysql_.*|valid MySQL result|MySqlClient\.)", re.I),
            re.compile(r"(PostgreSQL.*ERROR|Warning.*\Wpg_.*|valid PostgreSQL result|Npgsql\.)", re.I),
            re.compile(r"(Driver.* SQL[\-\_\ ]*Server|ODBC SQL.*Driver|SQLServer JDBC Driver|SQLServerException)", re.I),
            re.compile(r"(ORA-\d{5}|Oracle error|Oracle.*Driver|Warning.*\Woci_.*|Warning.*\Wora_.*)", re.I),
            re.compile(r"(Microsoft Access Driver|JET Database Engine|Access Database Engine)", re.I),
            re.compile(r"(SQLite/JDBCDriver|SQLite.Exception|System.Data.SQLite.SQLiteException)", re.I),
            re.compile(r"(Sybase message|Sybase.*Server message|SybSQLException|TDS error)", re.I),
            re.compile(r"Syntax error in SQL statement|You have an error in your SQL syntax", re.I)
        ]

    def check(self, response_text, url, payload=None):
        findings = []
        for pattern in self.error_patterns:
            match = pattern.search(response_text)
            if match:
                findings.append({
                    "Type": "SQL Injection",
                    "Endpoint": url,
                    "Severity": "CRITICAL",
                    "Evidence": {
                        "Payload": payload,
                        "Response_Match": match.group(0)[:100] + "..."
                    }
                })
                break # One hit is enough to flag endpoint
        return findings

class XSSDetector:
    def __init__(self):
        # Standard Canary
        self.canary = '"><script>confirm(1337)</script>'

    def check(self, response_text, url, payload=None):
        findings = []
        if payload and self.canary in payload:
            if self.canary in response_text:
                findings.append({
                    "Type": "Reflected XSS",
                    "Endpoint": url,
                    "Severity": "HIGH",
                    "Evidence": {
                         "Payload": self.canary,
                         "Response_Match": "Canary found unescaped in response"
                    }
                })
        return findings

class MassAssignmentDetector:
    def check(self, baseline_resp, fuzzed_resp, endpoint):
        """
        Compare baseline and fuzzed responses to detect deviations.
        baseline_resp/fuzzed_resp: dict with keys {'size', 'latency', 'status'}
        """
        findings = []
        
        # Ignore static assets for mass assignment
        if endpoint.endswith(('.js', '.css', '.png', '.jpg', '.woff', '.ico')):
            return []

        evidence = {}
        is_suspicious = False

        # 1. Status Code Detection
        if fuzzed_resp['status'] != baseline_resp['status']:
             is_suspicious = True
             evidence['Status_Change'] = f"{baseline_resp['status']} -> {fuzzed_resp['status']}"

        # 2. Size Deviation Detection (> 5%)
        # Ensure we don't divide by zero
        base_size = max(1, baseline_resp['size']) 
        size_diff = abs(fuzzed_resp['size'] - base_size)
        size_percent = size_diff / base_size
        
        if size_percent > 0.05:
             is_suspicious = True
             evidence['Size_Deviation'] = f"{baseline_resp['size']} -> {fuzzed_resp['size']} bytes ({size_percent*100:.1f}%)"

        if is_suspicious:
            findings.append({
                 "Type": "Mass Assignment Vulnerability",
                 "Endpoint": endpoint,
                 "Risk": "HIGH", # Prompt says HIGH, previous code said Critical. Aligning with Prompt.
                 "Evidence": evidence
            })
            
        return findings
