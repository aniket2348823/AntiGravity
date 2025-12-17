# Phase 10: Advanced Scanning & Reporting Upgrade

## User Review Required
> [!IMPORTANT]
> This upgrade introduces active vulnerability scanning (SQL Injection, XSS payloads). While these checks are non-destructive, scanning targets you do not own may be considered hostile. Ensure you have permission to scan the target URL.

## Proposed Changes

### Backend Logic (`scan_engine.py`)
- [MODIFY] Upgrade `run_scan` method to include:
    - **Robust Connection Handling**: `verify=False` for SSL, timeouts, and `try-except` blocks for connection errors.
    - **Header Analysis**: Expand current checks (HSTS, CSP, X-Frame-Options, Server Leakage).
    - **SQL Injection**: Test query params (if any) with basic payloads like `' OR '1'='1`.
    - **XSS**: Test info reflection with `<script>alert(1)</script>`.
    - **Directory Enumeration**: Check for sensitive paths: `/.env`, `/.git`, `/admin`, `/backup`, `/robots.txt`.
    - **Port Check**: Basic check of 80, 443, 8080.

### PDF Reporting (`pdf_generator.py`)
- [MODIFY] Rewrite `generate_scan_report` to produce a professional report:
    - **Title Page**: Scan ID, Target, Date, Overall Risk Score.
    - **Executive Summary**: High-level overview of findings.
    - **Vulnerability Details**: For each finding:
        - **Severity** (High/Medium/Low)
        - **Description**
        - **Recommendation**
    - **Technical Details**: Request/Response snippets if available.

### Dependencies (`backend/requirements.txt`)
- [MODIFY] Ensure `requests` is present (already done).

## Verification Plan

### Automated Verification
- Run backend tests (manual execution of `scan_engine.py` methods or via API).
- Generate a report for a test scan and inspect the PDF visually.

### Manual Verification
- Start Flask + Frontend.
- Scan `http://testphp.vulnweb.com` (a legal test target) or `http://localhost`.
- Verify no "Connection Failed" errors for valid sites.
- Download PDF and check for professional layout and detailed findings.
