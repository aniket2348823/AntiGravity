import requests
import json

def check_history():
    try:
        r = requests.get("http://localhost:5000/api/history")
        data = r.json()
        print(f"Total Scans in History: {len(data)}")
        
        for i, scan in enumerate(data[:3]): # Show top 3
            res = json.loads(scan['result'])
            vulns = res.get('vulnerabilities', [])
            target = res.get('target', 'unknown')
            print(f"Scan #{scan['id']} [{target}]: {len(vulns)} findings")
            
            # Check for heavy vector existence
            heavy_count = sum(1 for v in vulns if v['Type'] in ['Existential Reality Risk', 'Neutrino-Emission Leak', 'Temporal Paradox (STL)'])
            print(f"  > Heavy/God Vectors found: {heavy_count}")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_history()
