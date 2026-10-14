import {
  Agent,
  Message,
  MessageAttachment,
  OutboundAttachmentInput,
  ReviewItem,
  Stats,
  Domain,
  SmtpConfig,
  ApiKeyItem,
  ApiKeyCreated,
  OutboundJob,
  OutboundJobStatus,
  OutboundRetryEvent
} from "./types";

const API_BASE = "/api/backend";

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

  getMessageAttachments: (agentEmail: string, messageId: string) =>
    request<MessageAttachment[]>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages/${messageId}/attachments`),

  sendMessage: (
    agentEmail: string,
    data: { recipient: string; subject: string; body_text: string; body_html?: string; thread_id?: string; attachments?: OutboundAttachmentInput[] },
    idempotencyKey?: string,
  ) =>
    request<Message>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages`, {
      method: "POST",
      headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : undefined,
      body: JSON.stringify(data),
    }),

  replyMessage: (
    agentEmail: string,
    messageId: string,
    data: { body_text: string; body_html?: string; attachments?: OutboundAttachmentInput[] },
    idempotencyKey?: string,
  ) =>
    request<Message>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages/${messageId}/reply`, {
      method: "POST",
      headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : undefined,
      body: JSON.stringify(data),
    }),

  forwardMessage: (agentEmail: string, messageId: string, data: { recipient: string; note?: string }) =>
    request<Message>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages/${messageId}/forward`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getThread: (agentEmail: string, threadId: string) =>
    request<Message[]>(`/v1/agents/${encodeURIComponent(agentEmail)}/messages/thread/${encodeURIComponent(threadId)}`),

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

  // Domains & DNS
  getDomains: () => request<Domain[]>("/v1/domains"),
  createDomain: (domain: string) =>
    request<Domain>("/v1/domains", {
      method: "POST",
      body: JSON.stringify({ domain }),
    }),
  verifyDomain: (domain: string) =>
    request<Domain>(`/v1/domains/${encodeURIComponent(domain)}/verify`, {
      method: "POST",
    }),
  deleteDomain: (domain: string) =>
    request<void>(`/v1/domains/${encodeURIComponent(domain)}`, {
      method: "DELETE",
    }),

  // Upstream SMTP Relay Settings
  getSmtpConfig: () => request<SmtpConfig>("/v1/settings/smtp"),
  updateSmtpConfig: (data: Partial<SmtpConfig>) =>
    request<SmtpConfig>("/v1/settings/smtp", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  testSmtpConnection: (test_recipient: string) =>
    request<{ success: boolean; message: string }>("/v1/settings/smtp/test", {
      method: "POST",
      body: JSON.stringify({ test_recipient }),
    }),

  // API Keys
  getApiKeys: () => request<ApiKeyItem[]>("/v1/api-keys"),
  createApiKey: (name: string, agent_email: string, scope: string = "full_access", expires_in_days: number | null = 90) =>
    request<ApiKeyCreated>("/v1/api-keys", {
      method: "POST",
      body: JSON.stringify({ name, agent_email, scope, expires_in_days }),
    }),
  deleteApiKey: (id: string) =>
    request<void>(`/v1/api-keys/${id}`, {
      method: "DELETE",
    }),

  // Outbound delivery queue
  getOutboundJobs: (status?: OutboundJobStatus, limit = 100) => {
    const params = new URLSearchParams({ limit: String(Math.min(Math.max(limit, 1), 200)) });
    if (status) params.set("status", status);
    return request<OutboundJob[]>(`/v1/outbox?${params.toString()}`);
  },
  retryOutboundJob: (jobId: string, confirmDuplicateRisk = false) => {
    const qs = confirmDuplicateRisk ? "?confirm_duplicate_risk=true" : "";
    return request<OutboundJob>(`/v1/outbox/${encodeURIComponent(jobId)}/retry${qs}`, { method: "POST" });
  },
  getOutboundRetryEvents: (jobId: string, limit = 50) => {
    const params = new URLSearchParams({ limit: String(Math.min(Math.max(limit, 1), 200)) });
    return request<OutboundRetryEvent[]>(`/v1/outbox/${encodeURIComponent(jobId)}/retries?${params.toString()}`);
  },

  // MCP Info
  getMcpInfo: () => request<Record<string, unknown>>("/mcp/info"),
};
