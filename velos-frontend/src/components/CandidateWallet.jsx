import React, { useState } from 'react';
import { ShieldCheck, Download, CreditCard, Lock, Share2, Search, ArrowRight } from 'lucide-react';

const CandidateWallet = () => {
    const [activeTab, setActiveTab] = useState('credentials');

    const mockCredentials = [
        { id: 1, type: "Backend Developer Pipeline", match: 92, trust: 88, status: "Verified", date: "2025-01-15", uri: "zynd://cred/abc1234x9" },
        { id: 2, type: "React/Nextjs Frontend", match: 74, trust: 95, status: "Pending Payment", date: "2025-01-14", uri: "zynd://cred/xyz9876p0" }
    ];

    return (
        <div className="w-full space-y-6">
            <div className="flex justify-between items-center bg-white/50 backdrop-blur-md p-6 rounded-3xl border border-white/60 shadow-lg">
                <div>
                    <h2 className="text-3xl font-black bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">Zynd Decentralized Wallet</h2>
                    <p className="text-gray-600 mt-2">Manage your cryptographic W3C skill credentials & payments</p>
                </div>
                <div className="flex space-x-4">
                    <button className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold transition-all shadow-lg flex items-center gap-2">
                        <Share2 size={18} /> Export Profile
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {mockCredentials.map(cred => (
                    <div key={cred.id} className="bg-white/40 backdrop-blur-lg border border-purple-200 p-6 rounded-2xl shadow-xl hover:shadow-purple-500/20 transition-all">
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl shadow-inner">
                                <ShieldCheck className="text-white" size={24} />
                            </div>
                            <span className={`px-3 py-1 text-xs font-bold rounded-full ${cred.status === 'Verified' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}`}>
                                {cred.status}
                            </span>
                        </div>
                        <h3 className="text-xl font-bold text-gray-800">{cred.type}</h3>
                        <p className="text-xs text-gray-500 font-mono mt-1 mb-4 truncate">{cred.uri}</p>

                        <div className="space-y-2 mb-6">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Skill Match</span>
                                <span className="font-bold text-indigo-600">{cred.match}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${cred.match}%` }}></div>
                            </div>
                        </div>

                        {cred.status === "Pending Payment" ? (
                            <button className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-xl font-bold shadow-lg flex items-center justify-center gap-2">
                                <CreditCard size={18} /> Pay $5 for W3C Minting
                            </button>
                        ) : (
                            <button className="w-full py-3 bg-white hover:bg-gray-50 text-purple-700 border border-purple-200 rounded-xl font-bold shadow flex items-center justify-center gap-2">
                                <Download size={18} /> Download Verified VC
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CandidateWallet;
