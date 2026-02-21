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
export const createWebSocket = (token: string, orgId: string) => {
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
