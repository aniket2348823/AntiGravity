import json
import datetime
from backend import pdf_generator
import os

mock_data = {
    "id": 1337,
    "timestamp": datetime.datetime.now().isoformat(),
    "result": json.dumps({
        "Scan_Report": {
            "Target": "https://api.target.com",
            "Vulnerabilities": [
                {
                    "Type": "Cross-Context Race Condition",
                    "Severity": "Critical",
                    "Endpoint": "https://api.target.com/v1/coupons/apply",
                    "Evidence": "REDEEMED 5 times in 2ms via Swarm Node 34.212.x.x"
                }
            ]
        }
    })
}

output = "test_strict_sovereign.pdf"
print(f"[*] Generating Strict Sovereign Report: {output}")
try:
    pdf_generator.generate_pdf(mock_data, output)
    if os.path.exists(output) and os.path.getsize(output) > 0:
         print("[+] Report generated successfully.")
    else:
         print("[-] Report file empty or missing.")
except Exception as e:
    print(f"[-] Failed to generate report: {e}")
