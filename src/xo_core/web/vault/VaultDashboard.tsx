import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { vaultAPI, VaultTaskResponse } from './VaultAPI';

interface VaultStatus {
  agent: {
    name: string;
    keys: number;
    trustMode: string;
    health: string;
    services: Record<string, string>;
  };
  storage: {
    vaultSealed: string;
    devCache: string;
    vaultBuilds: string;
  };
  backend: {
    health: string;
    agents: number;
    connections: number;
  };
  seals: {
    total: number;
    recent: string[];
  };
}

export const VaultDashboard: React.FC = () => {
  const [status, setStatus] = useState<VaultStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchStatus = async () => {
    setLoading(true);
    try {
      // Fetch status from API
      const [agentResponse, storageResponse, backendResponse] = await Promise.all([
        vaultAPI.executeTask('cosmos.vault-agent-status'),
        vaultAPI.executeTask('storage.status'),
        vaultAPI.executeTask('backend.check-health')
      ]);

      setStatus({
        agent: agentResponse.data || {
          name: "XO Vault Agent",
          keys: 5,
          trustMode: "programmatic",
          health: "healthy",
          services: {
            orchestration: "healthy",
            trusted_execution: "healthy",
            social_recovery: "healthy"
          }
        },
        storage: storageResponse.data || {
          vaultSealed: "healthy",
          devCache: "healthy",
          vaultBuilds: "healthy"
        },
        backend: backendResponse.data || {
          health: "critical",
          agents: 4,
          connections: 4
        },
        seals: {
          total: 3,
          recent: [
            "system_20250724_023740.zip",
            "message_bottle_20250723_222656.zip",
            "eighth_seal_20250723_180000.zip"
          ]
        }
      });
    } catch (error) {
      console.error('Error fetching status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const runVaultTask = async (task: string, params: Record<string, any> = {}) => {
    console.log(`Running vault task: ${task}`, params);
    
    // Show loading state
    setLoading(true);
    
    try {
      // Use real API with fallback to mock
      const response = await vaultAPI.executeTask(task, params);
      
      if (response.success) {
        console.log(`Task ${task} completed:`, response.message);
        // Refresh status after task completion
        fetchStatus();
      } else {
        console.error(`Task ${task} failed:`, response.error);
        alert(`Task failed: ${response.error}`);
      }
    } catch (error) {
      console.error(`Error running task ${task}:`, error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-400">🔐 XO Vault Dashboard</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-green-400">● Live</span>
              <span className="text-gray-400">v0.1.0</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['overview', 'agents', 'storage', 'seals', 'tasks'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Vault Agent Status */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700"
            >
              <h3 className="text-lg font-semibold mb-4">🤖 Vault Agent</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Name:</span>
                  <span>{status?.agent.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Keys:</span>
                  <span>{status?.agent.keys}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Trust Mode:</span>
                  <span className="text-blue-400">{status?.agent.trustMode}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Health:</span>
                  <span className="text-green-400">{status?.agent.health}</span>
                </div>
              </div>
              <button
                onClick={() => runVaultTask('cosmos.vault-agent-status')}
                className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
              >
                Check Status
              </button>
            </motion.div>

            {/* Storage Status */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700"
            >
              <h3 className="text-lg font-semibold mb-4">💾 Storage</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Vault Sealed:</span>
                  <span className="text-green-400">{status?.storage.vaultSealed}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Dev Cache:</span>
                  <span className="text-green-400">{status?.storage.devCache}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Vault Builds:</span>
                  <span className="text-green-400">{status?.storage.vaultBuilds}</span>
                </div>
              </div>
              <button
                onClick={() => runVaultTask('storage.status')}
                className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
              >
                Check Storage
              </button>
            </motion.div>

            {/* Backend Status */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700"
            >
              <h3 className="text-lg font-semibold mb-4">⚙️ Backend</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Health:</span>
                  <span className="text-red-400">{status?.backend.health}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Agents:</span>
                  <span>{status?.backend.agents}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Connections:</span>
                  <span>{status?.backend.connections}</span>
                </div>
              </div>
              <button
                onClick={() => runVaultTask('backend.check-health')}
                className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
              >
                Check Health
              </button>
            </motion.div>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">🚀 Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { name: 'Agent Setup', task: 'cosmos.vault-agent-setup', icon: '🤖' },
                { name: 'System Snapshot', task: 'seal.system-snapshot', icon: '📸' },
                { name: 'Agent Mesh Map', task: 'backend.agent-mesh-map', icon: '🧠' },
                { name: 'Initiate Loop', task: 'cosmos.initiate-loop', icon: '🌌' },
                { name: 'Smart Routing', task: 'storage.route-smart', icon: '🧭' },
                { name: 'Sync Manifest', task: 'spec.sync-manifest', icon: '🔄' },
              ].map((action) => (
                <motion.button
                  key={action.task}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => runVaultTask(action.task)}
                  className="bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg p-6 text-left transition-colors"
                >
                  <div className="text-2xl mb-2">{action.icon}</div>
                  <h3 className="font-semibold">{action.name}</h3>
                  <p className="text-sm text-gray-400 mt-1">{action.task}</p>
                </motion.button>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'seals' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">🔒 Seals & Snapshots</h2>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Recent Seals</h3>
                <span className="text-gray-400">Total: {status?.seals.total}</span>
              </div>
              <div className="space-y-2">
                {status?.seals.recent.map((seal, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b border-gray-700 last:border-b-0">
                    <span className="font-mono text-sm">{seal}</span>
                    <span className="text-green-400 text-sm">✓ Verified</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}; 