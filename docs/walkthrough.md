# Walkthrough - Advanced API Endpoint Scanner

## Overview
This document guides you through verifying the **Advanced API Endpoint Scanner**. The system now includes a robust scanning engine (SQLi, XSS, Directory Enumeration) and generates professional PDF reports.

## Prerequisites
- **Backend Running**: `python app.py` (Port 5000)
- **Frontend Running**: `npm run dev` (Port 5173)

**Note**: Project folder moved to `d:\Antigravity 2\api endpoint scanner`.


## Verification Steps (Phase 10)

### 1. New Scan Interface
1.  Open `http://localhost:5173`.
2.  Navigate to the **New Scan** tab.
3.  Enter a target URL.
    -   *Safe Test*: `http://testphp.vulnweb.com` (Intentionally vulnerable)
    -   *Connectivity Test*: `http://example.com`

### 2. Verify Advanced Engine (Phase 11: Real-Time & Crawler)
1.  Click **Launch Scan**.
2.  **Live Console**: Watch the black "Live Scan Console" box. It should instantly start scrolling with messages like:
    -   `[10:00:01] Initializing scan for...`
    -   `[10:00:03] Connectivity OK. Launching Crawler...`
    -   `[10:00:05] Crawling: http://target.com/about`
3.  **Deep Scanning**: The scanner will now find links on the page and test them too (Depth: 2).
4.  **New Checks**: Watch for "Testing LFI" or "Testing Open Redirect" in the logs.

### 3. Professional Reporting
1.  Go to the **Findings** (History) tab.
2.  Wait for the scan to complete.
3.  Click **Download PDF**.
4.  **Open the PDF**. It should now feature:
    -   **Title Page**: With Scan ID, Target, and Timestamp.
    -   **Executive Summary**: A high-level overview of risk.
    -   **Detailed Findings**: Categorized by name, severity, and including **Remediation Advice**.

## Troubleshooting
- **"Connection Failed"**: The new engine handles this gracefully. If scanning fails, the report will list "Connection Failed" as a Critical finding with the specific error error.
