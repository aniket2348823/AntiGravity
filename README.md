# Antigravity API Endpoint Scanner

## Overview
A comprehensive, automated web vulnerability scanner designed to identify common security flaws in API endpoints and web applications. It combines passive analysis with active probing to deliver professional-grade security assessments.

## Key Capabilities

### 1. Security Header Analysis (Passive)
Audit of HTTP response headers to ensure best practices are enforced.
- **Checks**: `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`.
- **Purpose**: Prevents Clickjacking, MIME-sniffing, and Protocol Downgrade attacks.

### 2. Active Vulnerability Detection
Safe, non-destructive payloads to test for critical flaws.
- **SQL Injection (SQLi)**: Tests query parameters for database access vulnerabilities.
- **Cross-Site Scripting (Reflected XSS)**: Checks if the application unsafely reflects user input.
- **Directory Enumeration**: Scans for hidden or exposed sensitive files (e.g., `/.env`, `/admin`, `/.git`, `/backup`).
- **Secret Leaks**: Identifies exposed API keys or configuration files.

### 3. Server Reconnaissance
- **Information Leakage**: Detects exposed server versions (e.g., "Nginx 1.18", "IIS 8.5") which help attackers target specific exploits.
- **HTTP Method Auditing**: Identifies unsafe methods like `PUT`, `DELETE`, or `TRACE` that should be disabled.
- **Port Scanning**: Verifies accessibility of standard web ports.

### 4. Professional Reporting
- Generates detail PDF reports after each scan.
- Includes **Executive Summary**, **Risk Grading** (Critical to Low), and specific **Remediation Advice**.

## Usage
1.  **Start Backend**: `python backend/app.py`
2.  **Start Frontend**: `cd frontend && npm run dev`
3.  **Launch**: Open provided URL (e.g., `http://localhost:5173`).
4.  **Scan**: Enter Target URL in the dashboard.
5.  **Report**: Download PDF from the Findings tab.
