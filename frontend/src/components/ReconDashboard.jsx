import React, { useState, useEffect } from 'react';

const ReconDashboard = () => {
    const [stats, setStats] = useState({
        activeNodes: 0,
        totalRequests: 0,
        qRewards: 0,
        criticalHits: 0,
        swarmStatus: 'IDLE'
    });

    const [nodes, setNodes] = useState([]);

    // Transform raw data into a visual grid for the "Warhead" map
    useEffect(() => {
        // Poll for stats (Simulation of real-time socket)
        const interval = setInterval(() => {
            // Mock data fetch - in real app, fetch from /api/status or socket
            fetch('http://localhost:5000/api/status')
                .then(res => res.json())
                .then(data => {
                    // Simulate swarm activity based on scan status
                    const isScanning = data.status === 'Running';
                    setStats({
                        activeNodes: isScanning ? Math.floor(Math.random() * 50) + 10 : 0,
                        totalRequests: data.progress ? parseInt(data.progress) * 5 : 0, // rough estimate
                        qRewards: isScanning ? Math.floor(Math.random() * 500) : stats.qRewards,
                        criticalHits: data.findings ? data.findings.length : 0,
                        swarmStatus: isScanning ? 'ACTIVE' : 'IDLE'
                    });

                    if (isScanning) {
                        // Generate mock node grid
                        const newNodes = Array(12).fill(0).map((_, i) => ({
                            id: i,
                            region: ['us-east-1', 'eu-west-1', 'ap-south-1'][i % 3],
                            status: Math.random() > 0.2 ? 'HIT' : 'ROTATING',
                            ip: `10.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.x`
                        }));
                        setNodes(newNodes);
                    } else {
                        setNodes([]);
                    }
                })
                .catch(err => console.error("Dashboard Sync Error:", err));
        }, 2000);
        return () => clearInterval(interval);
    }, [stats.qRewards]);

    return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 shadow-2xl mb-8">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                    Aether-Singularity Omniscient Dashboard
                </h2>
                <div className={`px-4 py-1 rounded-full text-xs font-mono font-bold tracking-widest ${stats.swarmStatus === 'ACTIVE'
                    ? 'bg-red-900 text-red-200 animate-pulse border border-red-500'
                    : 'bg-green-900 text-green-200 border border-green-500'
                    }`}>
                    SWARM: {stats.swarmStatus}
                </div>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-gray-800 p-4 rounded-md border border-gray-700">
                    <p className="text-gray-400 text-sm uppercase tracking-wider">Active Warheads</p>
                    <p className="text-3xl font-mono text-blue-400">{stats.activeNodes}</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-md border border-gray-700">
                    <p className="text-gray-400 text-sm uppercase tracking-wider">Q-Learning Rewards</p>
                    <p className="text-3xl font-mono text-yellow-400">{stats.qRewards}</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-md border border-gray-700">
                    <p className="text-gray-400 text-sm uppercase tracking-wider">Total Burst Req</p>
                    <p className="text-3xl font-mono text-purple-400">{stats.totalRequests.toLocaleString()}</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-md border border-gray-700">
                    <p className="text-gray-400 text-sm uppercase tracking-wider">Critical Impacts</p>
                    <p className="text-3xl font-mono text-red-500">{stats.criticalHits}</p>
                </div>
            </div>

            {/* Swarm Visualization Grid */}
            <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
                <h3 className="text-sm font-semibold text-gray-400 mb-4 flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    Global Ephemeral Nodes (Live)
                </h3>

                {nodes.length > 0 ? (
                    <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                        {nodes.map((node) => (
                            <div key={node.id} className="relative group bg-gray-900 p-2 rounded border border-gray-700 hover:border-blue-500 transition-colors">
                                <div className="flex justify-between items-start">
                                    <span className="text-[10px] text-gray-500">{node.region}</span>
                                    <div className={`w-1.5 h-1.5 rounded-full ${node.status === 'HIT' ? 'bg-green-400' : 'bg-yellow-500 animate-spin'}`}></div>
                                </div>
                                <div className="mt-1 font-mono text-xs text-blue-300">{node.ip}</div>
                                <div className="absolute inset-0 bg-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8 text-gray-600 italic">
                        Swarm Idle. Waiting for sovereign command...
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReconDashboard;
