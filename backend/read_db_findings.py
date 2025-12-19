import sqlite3
import json

conn = sqlite3.connect('backend/scan_history.db')
c = conn.cursor()
c.execute("SELECT result FROM scans ORDER BY id DESC LIMIT 1")
row = c.fetchone()
if row:
    result_json = row[0]
    if result_json:
        result = json.loads(result_json)
        # Check structure
        # Omnibus structure: {"Scan_Report": {"Vulnerabilities": [...]}}
        vulns = []
        if "Scan_Report" in result:
             vulns = result["Scan_Report"].get("Vulnerabilities", [])
        elif "vulnerabilities" in result: # Old format fallback
             vulns = result.get("vulnerabilities", [])
             
        print(f"Total Findings in DB: {len(vulns)}")
        for v in vulns:
             print(f"Keys: {list(v.keys())}")
             print(f"[{v.get('Type', v.get('name'))}] {v.get('Endpoint', v.get('url'))} - {v.get('Severity', v.get('severity'))}")
    else:
        print("Last scan has no result data.")
else:
    print("No scans found in DB.")
conn.close()
