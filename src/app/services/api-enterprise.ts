/**
 * Enterprise API service for NitiLens Platform
 * Multi-tenant, multi-policy support with authentication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Authentication
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  register: async (data: { email: string; password: string; full_name: string; org_name: string }) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  getMe: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};

// Policies
export const policiesAPI = {
  list: async (token: string, filters?: { department?: string; framework?: string }) => {
    const params = new URLSearchParams(filters as any);
    const response = await fetch(`${API_BASE_URL}/api/policies?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  upload: async (token: string, file: File, metadata: any) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });

    const response = await fetch(`${API_BASE_URL}/api/policies/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    });
    return response.json();
  },

  compare: async (token: string, policyId1: string, policyId2: string) => {
    const response = await fetch(
      `${API_BASE_URL}/api/policies/compare?policy1=${policyId1}&policy2=${policyId2}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    return response.json();
  },

  delete: async (token: string, policyId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/policies/${policyId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};

// Connectors
export const connectorsAPI = {
  list: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/connectors/list`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  add: async (token: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/connectors/add`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  test: async (token: string, connectorId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/connectors/test/${connectorId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  remove: async (token: string, connectorId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/connectors/remove/${connectorId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};

// Compliance
export const complianceAPI = {
  scan: async (token: string, options: {
    connector_id?: string;
    department?: string;
    framework?: string;
    limit?: number;
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/compliance/scan`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });
    return response.json();
  },

  getViolations: async (token: string, filters?: {
    policy_id?: string;
    department?: string;
    severity?: string;
    status?: string;
  }) => {
    const params = new URLSearchParams(filters as any);
    const response = await fetch(`${API_BASE_URL}/api/compliance/violations?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getSummary: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/compliance/summary`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};

// Monitoring
export const monitoringAPI = {
  health: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  stats: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/stats`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  metrics: async () => {
    const response = await fetch(`${API_BASE_URL}/metrics`);
    return response.text();
  },
};

// WebSocket
export const createWebSocket = (token: string) => {
  const wsUrl = API_BASE_URL.replace('http', 'ws');
  const ws = new WebSocket(`${wsUrl}/ws?token=${token}`);

  ws.onopen = () => {
    console.log('WebSocket connected');
    // Send heartbeat every 30 seconds
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      }
    }, 30000);
  };

  return ws;
};

export default {
  authAPI,
  policiesAPI,
  connectorsAPI,
  complianceAPI,
  monitoringAPI,
  createWebSocket,
};

// Dashboard
export const dashboardAPI = {
  getFeatureStatus: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/feature-status`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getOverview: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/overview`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};

// Remediation
export const remediationAPI = {
  getCases: async (token: string, filters?: {
    status?: string;
    priority?: string;
    assigned_to?: string;
  }) => {
    const params = new URLSearchParams(filters as any);
    const response = await fetch(`${API_BASE_URL}/api/remediation?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getCaseDetails: async (token: string, caseId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/remediation/${caseId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  updateStatus: async (token: string, caseId: string, status: string, comment?: string) => {
    const response = await fetch(`${API_BASE_URL}/api/remediation/update-status/${caseId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status, comment }),
    });
    return response.json();
  },

  addComment: async (token: string, caseId: string, comment: string) => {
    const response = await fetch(`${API_BASE_URL}/api/remediation/comment/${caseId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ comment_text: comment }),
    });
    return response.json();
  },

  getSummary: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/remediation/stats/summary`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};

// Risk & Anomaly Detection
export const riskAPI = {
  getAnomalies: async (token: string, threshold = 0.75, limit = 100) => {
    const response = await fetch(
      `${API_BASE_URL}/api/risk/anomalies?threshold=${threshold}&limit=${limit}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    return response.json();
  },

  getHeatmap: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/risk/heatmap`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getTrend: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/risk/trend`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getDashboard: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/risk/dashboard`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  trainModel: async (token: string, limit = 1000) => {
    const response = await fetch(`${API_BASE_URL}/api/risk/train-model`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ limit }),
    });
    return response.json();
  },
};

// Policy Impact Analysis
export const policyImpactAPI = {
  analyze: async (token: string, oldPolicyId: string, newPolicyId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/policy-impact/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        old_policy_id: oldPolicyId,
        new_policy_id: newPolicyId,
      }),
    });
    return response.json();
  },

  getHistory: async (token: string, policyId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/policy-impact/history/${policyId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getReport: async (token: string, policyId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/policy-impact/report/${policyId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};

// Subscription Management
export const subscriptionAPI = {
  getCurrent: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/subscription/current`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getUsage: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/subscription/usage`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  listPlans: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/subscription/plans`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  upgrade: async (token: string, planName: string) => {
    const response = await fetch(`${API_BASE_URL}/api/subscription/upgrade`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ plan_name: planName }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upgrade plan');
    }
    return response.json();
  },

  cancel: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/subscription/cancel`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to cancel subscription');
    }
    return response.json();
  },
};

// NitiGuard AI Agent
export const agentAPI = {
  chat: async (token: string, message: string, conversationId?: string | null, isVoice = false) => {
    const response = await fetch(`${API_BASE_URL}/api/agent/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        is_voice: isVoice,
      }),
    });
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  },

  getHistory: async (token: string, conversationId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/agent/history/${conversationId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  executeAction: async (token: string, data: {
    message: string;
    action_type: string;
    target_id: string;
    conversation_id: string;
    confirmed: boolean;
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/agent/action`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
};
