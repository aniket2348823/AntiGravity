import requests
import json

try:
    res = requests.get('http://localhost:5000/api/history')
    data = res.json()
    last_scan = data[-1]
    result_json = json.loads(last_scan['result'])
    findings = result_json.get('vulnerabilities', [])
    
    print(f"Scan ID: {last_scan['id']}")
    print(f"Target: {last_scan['celery_id']}")
    print(f"Findings Count: {len(findings)}")
    for f in findings:
        print(f"- {f['name']} [{f['severity']}]")
except Exception as e:
    print(e)
