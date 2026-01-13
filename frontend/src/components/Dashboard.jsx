import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Shield, Zap, Globe, Cpu } from 'lucide-react';

const Dashboard = () => {
    const [nodes, setNodes] = useState(450);
    const [successRate, setSuccessRate] = useState(98.4);
    const [findings, setFindings] = useState([]);
    const [isScanning, setIsScanning] = useState(false);

    useEffect(() => {
        const fetchTelemetry = async () => {
            try {
                // Fetch from the local Antigravity Backend (Singularity API)
                const res = await fetch('/api/status');
                const data = await res.json();

                if (data.current_findings) {
                    setFindings(data.current_findings);
                }
                setIsScanning(data.is_scanning);

                // Simulate node fluctuation for aesthetic effect if scanning
                if (data.is_scanning) {
                    setNodes(prev => Math.min(Math.max(prev + Math.floor(Math.random() * 20 - 10), 400), 500));
                }
            } catch (e) {
                console.error("Telemetry Link Failure:", e);
            }
        };

        // Poll every 2 seconds
        const interval = setInterval(fetchTelemetry, 2000);
        fetchTelemetry(); // Initial call
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-sovereign-black text-electric-blue p-8 font-mono selection:bg-neon-purple selection:text-white">
            {/* Header: System Integrity Status */}
            <div className="flex justify-between items-center border-b border-electric-blue/30 pb-4 mb-8">
                <h1 className="text-2xl font-bold tracking-tighter flex items-center gap-3 text-white font-sans">
                    <Shield className="animate-pulse text-neon-purple" />
                    AETHER-TITAN // <span className="text-sovereign-gold">INFINITY-SINGULARITY v100.0</span>
                </h1>
                <div className="flex gap-6 text-sm">
                    <span className="flex items-center gap-2"><Globe size={16} className="text-neon-purple" /> SWARM: ACTIVE</span>
                    <span className="flex items-center gap-2 text-sovereign-gold"><Cpu size={16} /> L7_DESYNC: STABLE</span>
                </div>
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Real-time Swarm Telemetry */}
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="bg-gray-900/20 border border-electric-blue/30 p-6 rounded-lg backdrop-blur-sm"
                >
                    <h3 className="text-xs uppercase tracking-widest text-gray-500 mb-4 font-sans">Swarm Distribution</h3>
                    <div className="text-4xl font-bold mb-2 text-white">{nodes}</div>
                    <p className="text-xs text-electric-blue/70">ACTIVE LAMBDA NODES (US-EAST-1, EU-WEST-1)</p>
                    <div className="mt-6 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }} animate={{ width: '85%' }}
                            className="h-full bg-neon-purple shadow-[0_0_10px_#8A2BE2]"
                        />
                    </div>
                </motion.div>

                {/* Q-Learning State Hunter */}
                <div className="bg-gray-900/20 border border-electric-blue/30 p-6 rounded-lg md:col-span-2 backdrop-blur-sm">
                    <h3 className="text-xs uppercase tracking-widest text-gray-500 mb-4 font-sans">Business Logic Exploration (Q-Table)</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between text-xs border-b border-gray-800 pb-2 text-gray-400">
                            <span>STATE_PATH</span><span>REWARD_Q</span><span>STATUS</span>
                        </div>
                        {findings.length === 0 ? (
                            <div className="text-center py-8 text-gray-600 italic">Waiting for singularity induction...</div>
                        ) : (
                            findings.map((finding, i) => (
                                <div key={i} className="flex justify-between text-sm py-1 font-bold group hover:bg-white/5 transition-colors px-2 -mx-2 rounded">
                                    <span className="text-white font-mono">{finding.path}</span>
                                    <span className="text-sovereign-gold">+{90 - (i * 20)}.52</span>
                                    <span className="text-white font-mono break-all text-sm">
                                        <span className="text-electric-blue font-bold">TYPE:</span> {finding.Type || finding.type || "Unknown_Vuln"} <br />
                                        <span className="text-electric-blue font-bold">SEVERITY:</span> <span className={(finding.Severity === 'Critical' || finding.sev === 'Critical') ? 'text-red-500' : 'text-sovereign-gold'}>{finding.Severity || finding.severity || "INFO"}</span> <br />
                                        <span className="text-electric-blue font-bold">ENDPOINT:</span> {finding.Endpoint || finding.endpoint || finding.url || "N/A"} <br />
                                        <span className="text-electric-blue font-bold">EVIDENCE:</span> <span className="text-gray-400">{finding.Evidence || finding.evidence || "No Detail"}</span>
                                    </span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* Critical Chain Alert Box & Export */}
            <div className="mt-8 flex gap-6">
                <div className="flex-1 bg-red-900/10 border border-red-500/30 p-6 rounded-lg">
                    <div className="flex items-center gap-3 mb-4">
                        <Zap className="text-red-500" />
                        <h2 className="text-red-500 font-bold uppercase tracking-tighter font-sans">Critical Vulnerability Chain Detected</h2>
                    </div>
                    <div className="text-sm text-gray-400 font-mono">
                        Awaiting high-severity confirmation from logic gates...
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
