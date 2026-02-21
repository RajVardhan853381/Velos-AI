import React, { useEffect, useState } from 'react';
import { Network, Server, User, Cpu, ArrowRightLeft, ShieldAlert } from 'lucide-react';

const AgentGraph = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        // Simulated Orchestrator SSE Stream
        const mockEvents = [
            "Orchestrator: Initializing 7-Node Agent Mesh...",
            "Gatekeeper: Redacting PII from Candidate zynd-xyz...",
            "SkillValidator: Analyzing Context -> Match Score: 85.0%",
            "Inquisitor: Deploying Anti-Fraud Checks -> Trust Score: 60.0%",
            "Orchestrator: Discrepancy Detected (>20%). Invoking Agent Negotiation Protocol.",
            "SkillValidator: Arguing for candidate's GitHub repos...",
            "Inquisitor: Conceding 15 points based on repo depth evidence.",
            "BiasAuditor: Evaluating revised score for demographic neutrality. Passed.",
            "Publisher: Package sealed. Broadcasting to Zynd Mainnet."
        ];

        let i = 0;
        const interval = setInterval(() => {
            if (i < mockEvents.length) {
                setLogs(prev => [...prev, mockEvents[i]]);
                i++;
            } else {
                clearInterval(interval);
            }
        }, 1500);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full h-[800px] flex flex-col space-y-4">
            <div className="bg-white/50 backdrop-blur-md p-6 rounded-3xl border border-white/60 shadow-lg mb-4">
                <h2 className="text-3xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent flex items-center gap-3">
                    <Network size={32} className="text-blue-600" /> Multi-Agent Orchestrator
                </h2>
                <p className="text-gray-600 mt-2">Live visualization of autonomous negotiation protocols.</p>
            </div>

            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-slate-900 rounded-3xl border border-slate-700 p-8 shadow-2xl relative overflow-hidden flex flex-col items-center justify-center">
                    {/* Mock visual nodes for the hackathon */}
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.1)_0%,transparent_100%)]"></div>

                    <div className="grid grid-cols-3 gap-16 relative z-10 w-full max-w-2xl text-white">
                        <div className="flex flex-col items-center p-4 bg-slate-800 rounded-xl border border-blue-500/30">
                            <User size={32} className="text-blue-400 mb-2" />
                            <span className="font-bold text-sm">Gatekeeper</span>
                        </div>
                        <div className="flex flex-col items-center p-4 bg-slate-800 rounded-xl border border-purple-500/30 shadow-[0_0_30px_rgba(168,85,247,0.2)]">
                            <Server size={32} className="text-purple-400 mb-2 animate-pulse" />
                            <span className="font-bold text-sm">Orchestrator</span>
                        </div>
                        <div className="flex flex-col items-center p-4 bg-slate-800 rounded-xl border border-green-500/30">
                            <Cpu size={32} className="text-green-400 mb-2" />
                            <span className="font-bold text-sm">Publisher (Zynd)</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-32 relative z-10 w-full max-w-md mt-16 text-white">
                        <div className="flex flex-col items-center p-4 bg-slate-800 rounded-xl border border-orange-500/30">
                            <ArrowRightLeft size={32} className="text-orange-400 mb-2" />
                            <span className="font-bold text-sm">Validator</span>
                        </div>
                        <div className="flex flex-col items-center p-4 bg-slate-800 rounded-xl border border-red-500/30">
                            <ShieldAlert size={32} className="text-red-400 mb-2" />
                            <span className="font-bold text-sm">Inquisitor</span>
                        </div>
                    </div>
                </div>

                <div className="bg-black rounded-3xl p-6 font-mono text-xs overflow-y-auto border border-gray-800 shadow-2xl">
                    <div className="text-green-500 mb-4 border-b border-gray-800 pb-2 flex justify-between">
                        <span>TERMINAL // ROOT</span>
                        <span className="animate-pulse">● LIVE</span>
                    </div>
                    <div className="space-y-3">
                        {logs.map((log, idx) => (
                            <div key={idx} className={`${log.includes('Orchestrator') ? 'text-blue-400' :
                                    log.includes('Gatekeeper') ? 'text-gray-400' :
                                        log.includes('Validator') ? 'text-orange-400' :
                                            log.includes('Inquisitor') ? 'text-red-400' :
                                                log.includes('Auditor') ? 'text-yellow-400' : 'text-green-400'
                                }`}>
                                <span className="text-gray-600 mr-2">[{new Date().toISOString().split('T')[1].slice(0, 8)}]</span>
                                {log}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AgentGraph;
