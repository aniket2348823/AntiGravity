import { useState, useEffect } from 'react'
import './App.css'

function App() {
    const [isScanning, setIsScanning] = useState(false)
    const [history, setHistory] = useState([])
    const [statusMessage, setStatusMessage] = useState('')
    const [targetUrl, setTargetUrl] = useState('')

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/status')
            const data = await res.json()
            setIsScanning(data.is_scanning)
        } catch (err) {
            console.error("Failed to fetch status", err)
        }
    }

    const fetchHistory = async () => {
        try {
            const res = await fetch('/api/history')
            const data = await res.json()
            setHistory(data)
        } catch (err) {
            console.error("Failed to fetch history", err)
        }
    }

    useEffect(() => {
        fetchStatus()
        fetchHistory()
        const interval = setInterval(() => {
            fetchStatus()
            fetchHistory() // Polling for updates
        }, 2000)
        return () => clearInterval(interval)
    }, [])

    const startScan = async () => {
        if (!targetUrl) {
            setStatusMessage("Please enter a Target URL.")
            return
        }
        try {
            setStatusMessage("Starting scan...")
            const res = await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_url: targetUrl })
            })
            if (res.status === 409) {
                setStatusMessage("Scan already in progress.")
            } else if (res.ok) {
                setStatusMessage("Scan started.")
                setIsScanning(true)
            } else {
                setStatusMessage("Error starting scan.")
            }
            fetchHistory()
        } catch (err) {
            setStatusMessage("Network error.")
        }
    }

    const downloadReport = (scanId) => {
        window.open(`/api/report/${scanId}`, '_blank')
    }

    return (
        <div className="container">
            <h1>API Endpoint Scanner</h1>

            <div className="card">
                <h2>Control Panel</h2>
                <div className="input-group">
                    <input
                        type="text"
                        placeholder="Enter Target URL (e.g. https://google.com)"
                        value={targetUrl}
                        onChange={(e) => setTargetUrl(e.target.value)}
                        disabled={isScanning}
                    />
                </div>
                <p>Status: {isScanning ? <span className="running">Running</span> : <span className="idle">Idle</span>}</p>
                <button onClick={startScan} disabled={isScanning}>
                    {isScanning ? 'Scan in Progress...' : 'Start New Scan'}
                </button>
                {statusMessage && <p className="message">{statusMessage}</p>}
            </div>

            <div className="card">
                <h2>Scan History</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map(scan => (
                            <tr key={scan.id}>
                                <td>{scan.id}</td>
                                <td>{new Date(scan.timestamp).toLocaleString()}</td>
                                <td className={scan.status.toLowerCase()}>{scan.status}</td>
                                <td>
                                    {scan.status === 'Completed' && (
                                        <button onClick={() => downloadReport(scan.id)}>Download PDF</button>
                                    )}
                                </td>
                            </tr>
                        ))}
                        {history.length === 0 && <tr><td colSpan="4">No scans found.</td></tr>}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

export default App
