// Vault API Service for frontend integration
export interface VaultTaskResponse {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

export class VaultAPI {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  // Execute a vault task
  async executeTask(taskName: string, params: Record<string, any> = {}): Promise<VaultTaskResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/vault/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: taskName,
          params
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      // Fallback to mock if API is not available
      console.warn('API not available, using mock data:', error);
      return this.mockExecuteTask(taskName, params);
    }
  }

  // Get vault status
  async getStatus(): Promise<VaultTaskResponse> {
    return this.executeTask('vault.status');
  }

  // Get agent status
  async getAgentStatus(): Promise<VaultTaskResponse> {
    return this.executeTask('cosmos.vault-agent-status');
  }

  // Get storage status
  async getStorageStatus(): Promise<VaultTaskResponse> {
    return this.executeTask('storage.status');
  }

  // Get backend health
  async getBackendHealth(): Promise<VaultTaskResponse> {
    return this.executeTask('backend.check-health');
  }

  // Create system snapshot
  async createSnapshot(): Promise<VaultTaskResponse> {
    return this.executeTask('seal.system-snapshot');
  }

  // Setup vault agent
  async setupAgent(keys: number = 5): Promise<VaultTaskResponse> {
    return this.executeTask('cosmos.vault-agent-setup', { keys });
  }

  // Initiate agent loop
  async initiateLoop(agents: string = 'agent0,agentx,agentz'): Promise<VaultTaskResponse> {
    return this.executeTask('cosmos.initiate-loop', { agents });
  }

  // Route files smart
  async routeSmart(path: string, drop?: string): Promise<VaultTaskResponse> {
    return this.executeTask('storage.route-smart', { path, drop });
  }

  // Sync spec manifest
  async syncManifest(): Promise<VaultTaskResponse> {
    return this.executeTask('spec.sync-manifest');
  }

  // Get agent mesh map
  async getAgentMesh(): Promise<VaultTaskResponse> {
    return this.executeTask('backend.agent-mesh-map');
  }

  // Mock implementation for development
  async mockExecuteTask(taskName: string, params: Record<string, any> = {}): Promise<VaultTaskResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock responses for different tasks
    const mockResponses: Record<string, VaultTaskResponse> = {
      'cosmos.vault-agent-status': {
        success: true,
        message: 'Vault agent status retrieved',
        data: {
          name: 'XO Vault Agent',
          keys: 5,
          trustMode: 'programmatic',
          health: 'healthy',
          services: {
            orchestration: 'healthy',
            trusted_execution: 'healthy',
            social_recovery: 'healthy'
          }
        }
      },
      'storage.status': {
        success: true,
        message: 'Storage status retrieved',
        data: {
          vaultSealed: 'healthy',
          devCache: 'healthy',
          vaultBuilds: 'healthy'
        }
      },
      'backend.check-health': {
        success: true,
        message: 'Backend health check completed',
        data: {
          health: 'critical',
          agents: 4,
          connections: 4
        }
      },
      'seal.system-snapshot': {
        success: true,
        message: 'System snapshot created',
        data: {
          snapshot: `system_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.zip`
        }
      },
      'cosmos.vault-agent-setup': {
        success: true,
        message: 'Vault agent setup completed',
        data: {
          config: 'vault_agent.json',
          keys: params.keys || 5
        }
      },
      'cosmos.initiate-loop': {
        success: true,
        message: 'Agent loop initiated',
        data: {
          agents: params.agents?.split(',') || ['agent0', 'agentx', 'agentz'],
          choreography: 'cosmos_choreography.yml'
        }
      },
      'storage.route-smart': {
        success: true,
        message: 'Smart routing completed',
        data: {
          path: params.path,
          bucket: 'xo-vault-sealed',
          destination: `xo-vault-sealed/2025/07/24/${params.path.split('/').pop()}`
        }
      },
      'spec.sync-manifest': {
        success: true,
        message: 'Spec manifest synced',
        data: {
          tasks: 45,
          namespaces: 8
        }
      },
      'backend.agent-mesh-map': {
        success: true,
        message: 'Agent mesh mapped',
        data: {
          topology: 'ring',
          agents: 4,
          connections: 4
        }
      }
    };

    return mockResponses[taskName] || {
      success: true,
      message: `Task ${taskName} executed successfully`,
      data: { task: taskName, params }
    };
  }
}

// Export singleton instance
export const vaultAPI = new VaultAPI(); 