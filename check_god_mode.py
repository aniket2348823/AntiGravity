import asyncio
import sys
import os
import json
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock asyncio.sleep BEFORE importing the core
async def fast_sleep(delay):
    pass
asyncio.sleep = fast_sleep

from backend.antigravity.singularity_core import SingularityCore
from backend.pdf_generator import generate_pdf

def mock_log(msg):
    pass # Print only key phases to reduce noise
    if "PHASE" in msg or "GOD-TIER" in msg or "EXISTENTIAL" in msg or "ZENO" in msg:
        print(f"[TEST-LOG] {msg}")

def mock_finding(finding):
    if "Existential" in finding.get("Type", ""):
        print(f"[TEST-FINDING] {json.dumps(finding, indent=2)}")

async def test_god_tier():
    print("--- STARTING GOD-TIER VERIFICATION (FAST MODE) ---")
    core = SingularityCore(on_log=mock_log, on_finding=mock_finding)
    
    # Run the core (will trigger Phase 6)
    try:
        await core.run("test-timeline.io", scan_mode="Heavy")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- TESTING PDF GENERATION ---")
    mock_scan_data = {
        "id": 999,
        "timestamp": "2030-01-01 00:00:00",
        "result": json.dumps({
            "target": "test-timeline.io",
            "vulnerabilities": [
                {
                    "Type": "Existential Reality Risk",
                    "Endpoint": "[TIMELINE] Branch #042",
                    "Severity": "Critical",
                    "Evidence": "Timeline Divergence detected.",
                    "Analysis": "Ontological Stability: 0.0"
                }
            ]
        })
    }
    
    try:
        generate_pdf(mock_scan_data, "test_god_report.pdf")
        if os.path.exists("test_god_report.pdf"):
            print("PDF Generated Successfully: test_god_report.pdf")
        else:
            print("PDF Generation Failed: File not found")
    except Exception as e:
        print(f"PDF Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_god_tier())
