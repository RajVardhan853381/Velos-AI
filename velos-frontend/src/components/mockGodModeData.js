/**
 * Mock Data Injection Helper for GodMode Component
 * 
 * This file provides a temporary mock data function to inject test data
 * into the GodMode component for UI testing without backend dependency.
 * 
 * Usage:
 * 1. Import this in GodMode.jsx: import { injectMockData } from './mockGodModeData';
 * 2. Call in useEffect with a flag to toggle between real/mock data
 */

export const getMockInsights = () => ({
  bias_alerts: 0,
  fraud_cases: 0,
  avg_processing_time: 0,
  total_candidates: 0
});

export const getMockAgents = () => [
  {
    name: 'Gatekeeper',
    role: 'Entry Filter',
    status: 'idle',
    processed: 0,
    successRate: 0,
    avgTime: 0
  },
  {
    name: 'Validator',
    role: 'Verification',
    status: 'idle',
    processed: 0,
    successRate: 0,
    avgTime: 0
  },
  {
    name: 'Inquisitor',
    role: 'Deep Analysis',
    status: 'idle',
    processed: 0,
    successRate: 0,
    avgTime: 0
  }
];

export const getMockHealth = () => ({
  status: 'ready',
  uptime: 0,
  memory_usage: 0
});

/**
 * Complete mock data injection function
 * Call this instead of fetchGodModeData() for testing
 */
export const injectMockData = (setInsights, setAgents, setHealth, setLoading) => {
  console.log('🧪 Injecting mock data for testing...');
  
  setInsights(getMockInsights());
  setAgents(getMockAgents());
  setHealth(getMockHealth());
  setLoading(false);
  
  console.log('✅ Mock data injected successfully');
};

/**
 * HOW TO USE IN GodMode.jsx:
 * 
 * import { injectMockData } from './mockGodModeData';
 * 
 * // In your component:
 * useEffect(() => {
 *   const USE_MOCK_DATA = true; // Toggle this to switch between real/mock
 *   
 *   if (USE_MOCK_DATA) {
 *     injectMockData(setInsights, setAgents, setHealth, setLoading);
 *   } else {
 *     fetchGodModeData();
 *     const interval = setInterval(fetchGodModeData, 5000);
 *     return () => clearInterval(interval);
 *   }
 * }, []);
 */

export default {
  injectMockData,
  getMockInsights,
  getMockAgents,
  getMockHealth
};
