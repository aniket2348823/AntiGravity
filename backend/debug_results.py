import requests
import json

try:
    res = requests.get('http://localhost:5000/api/status')
    data = res.json()
    findings = data.get('current_findings', [])
    with open('findings.txt', 'w') as f:
        f.write(f"Total Findings: {len(findings)}\n")
        for finding in findings:
            f.write(f"[{finding.get('Type')}] {finding.get('Endpoint')} - {finding.get('Severity')}\n")
except Exception as e:
    print(e)
