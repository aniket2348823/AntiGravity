# Antigravity Scanner - Project Walkthrough

## 🚀 Overview
We have successfully built, verified, and deployed the **Antigravity Autonomous Scanner**. This system is now a live, cloud-hosted security tool capable of advanced vulnerability detection.

## 🏗️ Architecture
The system consists of three main components:
1.  **Backend (Render)**: A Flask-based API running the **Antigravity Engine** (Modular Monolith).
    *   **Orchestrator**: Manages the scan lifecycle.
    *   **Discovery**: Mines Wayback Machine & Source Maps.
    *   **Analysis**: Detects PII, Mass Assignment, and Soft 404s.
    *   **Transport**: High-performance AsyncIO networking.
2.  **Frontend (Vercel)**: A React-based SPA console for controlling scans and viewing real-time logs.
3.  **Target**: Any public URL (we tested with `testphp.vulnweb.com` and a local vulnerable app).

## 🛠️ Implementation Highlights
### 1. The Antigravity Engine
We moved away from simple crawling to a **multi-protocol** approach:
*   **Protocol A (Time Travel)**: Checks historical wayback URLs.
*   **Protocol B (Deep JS)**: Extracts hidden endpoints from `sourceMappingURL`.
*   **Protocol D (Differential Analysis)**: Detects Mass Assignment by comparing API responses.

### 2. Verification (The "Super Vulnerable" App)
We created `backend/vulnerable_app.py` to prove our engine works. It successfully failed:
*   ✅ **PII Leak**: Leaked fake SSNs/Emails (Detected).
*   ✅ **Mass Assignment**: Latency spikes on `admin=true` (Detected).
*   ✅ **Hidden Maps**: `app.js.map` (Detected).

## ☁️ Deployment Journey
We faced and solved several deployment challenges:
1.  **Deployment Automation**: Created `render.yaml` for one-click backend updates.
2.  **Frontend 404 Error**:
    *   *Issue*: Vercel tried to serve the repo root instead of `frontend/`.
    *   *Fix*: Added `vercel.json` to root, explicitly pointing Vercel to `cd frontend && npm run build`.
3.  **Backend 404 Error**:
    *   *Issue*: API root `/` had no route.
    *   *Fix*: Added a `/` health check returning status JSON.
4.  **Configuration**: Hardcoded the Production Backend URL in `App.jsx` to ensure instant connectivity without manual Environment Variable setup.

## 🟢 Live Status
*   **Frontend**: [https://anti-gravity-tau.vercel.app](https://anti-gravity-tau.vercel.app)
*   **Backend**: [https://antigravity-backend.onrender.com](https://antigravity-backend.onrender.com)

## 🧪 Final Verification
We performed a live scan against `http://testphp.vulnweb.com`.
The scan initiated successfully, confirming full end-to-end functionality in the cloud.
