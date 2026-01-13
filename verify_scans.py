import requests
import time
import json

API_URL = "http://localhost:5000/api"

def trigger_scan(mode):
    print(f"\n--- Triggering {mode} Scan ---")
    try:
        response = requests.post(f"{API_URL}/scan", json={"target_url": f"test-{mode.lower()}.local", "scan_mode": mode})
        if response.status_code == 200:
            print("Scan started successfully.")
            return True
        else:
            print(f"Failed to start scan: {response.text}")
            return False
    except Exception as e:
        print(f"Error triggering scan: {e}")
        return False

def wait_for_completion():
    print("Waiting for scan to complete...")
    while True:
        try:
            status = requests.get(f"{API_URL}/status").json()
            if status.get("status") == "idle":
                print("Scan completed.")
                return
            time.sleep(2)
        except Exception as e:
            print(f"Error polling status: {e}")
            time.sleep(2)

def get_latest_scan_details(mode):
    try:
        history = requests.get(f"{API_URL}/history").json()
        if not history:
            print("No history found.")
            return 0, []
        
        # Get latest scan
        latest = history[0]
        # The 'result' field is a stringified JSON
        result = json.loads(latest['result'])
        vulns = result.get('vulnerabilities', [])
        count = len(vulns)
        print(f"[{mode} Scan] Total Findings: {count}")
        
        # Check for specific high-end markers
        has_god_tier = any(v['Type'] == "Existential Reality Risk" for v in vulns)
        has_physics = any("Neutrino" in v['Type'] for v in vulns)
        has_logic_collapse = any("Logic Collapse" in v['Type'] for v in vulns)
        
        print(f"[{mode} Scan] Markers: God-Tier={has_god_tier}, Physics={has_physics}, High-End={has_logic_collapse}")
        return count, vulns
    except Exception as e:
        print(f"Error analyzing history: {e}")
        return 0, []

def main():
    # 1. Test Standard Scan
    if trigger_scan("Standard"):
        wait_for_completion()
        std_count, _ = get_latest_scan_details("Standard")
    else:
        std_count = 0

    # 2. Test Heavy Scan
    if trigger_scan("Heavy"):
        wait_for_completion()
        hvy_count, _ = get_latest_scan_details("Heavy")
    else:
        hvy_count = 0
        
    print("\n--- SUMMARY ---")
    print(f"Standard Scan Findings: {std_count}")
    print(f"Heavy Scan Findings:    {hvy_count}")
    print(f"Difference:             {hvy_count - std_count}")

if __name__ == "__main__":
    main()
