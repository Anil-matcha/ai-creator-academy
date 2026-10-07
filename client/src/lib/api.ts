import { Agent, Message, ReviewItem, Stats, ThreatScanResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Stats
  getStats: () => request<Stats>("/v1/stats"),

  // Agents
  getAgents: () => request<Agent[]>("/v1/agents"),
  getAgent: (email: string) => request<Agent>(`/v1/agents/${encodeURIComponent(email)}`),
  createAgent: (data: Partial<Agent>) =>
    request<Agent>("/v1/agents", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateAgent: (email: string, data: Partial<Agent>) =>
    request<Agent>(`/v1/agents/${encodeURIComponent(email)}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deleteAgent: (email: string) =>
    request<void>(`/v1/agents/${encodeURIComponent(email)}`, {
      method: "DELETE",
    }),

  // Messages
  getMessages: (
    agentEmail: string,
    filters?: { direction?: string; status?: string; thread_id?: string; limit?: number | string }
  ) => {
    const params = new URLSearchParams();
    if (filters?.direction) params.append("direction", filters.direction);
    if (filters?.status) params.append("status", filters.status);
    if (filters?.thread_id) params.append("thread_id", filters.thread_id);
    if (filters?.limit) params.append("limit", String(filters.limit));
    const qs = params.toString() ? `?${params.toString()}` : "";
    return request<Message[]>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages${qs}`);
  },

  getMessage: (agentEmail: string, messageId: string) =>
    request<Message>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages/${messageId}`),

  sendMessage: (
    agentEmail: string,
    data: { recipient: string; subject: string; body_text: string; body_html?: string; thread_id?: string }
  ) =>
    request<Message>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  replyMessage: (
    agentEmail: string,
    messageId: string,
    data: { body_text: string; body_html?: string }
  ) =>
    request<Message>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages/${messageId}/reply`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getThread: (agentEmail: string, threadId: string) =>
    request<Message[]>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages/thread/${threadId}`),

  // Reviews (HITL)
  getReviews: (status?: string) => {
    const qs = status ? `?status=${status}` : "";
    return request<ReviewItem[]>(`/v1/reviews${qs}`);
  },
  getReview: (reviewId: string) => request<ReviewItem>(`/v1/reviews/${reviewId}`),
  approveReview: (reviewId: string, notes?: string) =>
    request<ReviewItem>(`/v1/reviews/${reviewId}/approve`, {
      method: "POST",
      body: JSON.stringify({ action: "approve", notes }),
    }),
  rejectReview: (reviewId: string, notes?: string) =>
    request<ReviewItem>(`/v1/reviews/${reviewId}/reject`, {
      method: "POST",
      body: JSON.stringify({ action: "reject", notes }),
    }),

  // Simulator
  simulateInbound: (data: {
    agent_email: string;
    sender: string;
    subject: string;
    body_text: string;
    body_html?: string;
    spf_status?: string;
    dkim_status?: string;
    dmarc_status?: string;
    verified_domain?: string;
  }) =>
    request<{
      message: Message;
      threat_scan: ThreatScanResult;
      action_taken: string;
      review_id?: string;
    }>("/v1/simulate/inbound", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  evaluateThreat: (data: {
    subject: string;
    body_text: string;
    body_html?: string;
    sensitivity?: string;
  }) => {
    const params = new URLSearchParams();
    if (data.subject) params.append("subject", data.subject);
    if (data.body_text) params.append("body_text", data.body_text);
    if (data.body_html) params.append("body_html", data.body_html);
    if (data.sensitivity) params.append("sensitivity", data.sensitivity);
    return request<ThreatScanResult>(`/v1/simulate/threat-eval?${params.toString()}`, {
      method: "POST",
    });
  },

  // MCP Info
  getMcpInfo: () => request<Record<string, unknown>>("/mcp/info"),
};
