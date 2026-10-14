export interface Agent {
  id: string;
  email: string;
  display_name: string;
  description: string;
  status: "active" | "paused";
  threat_sensitivity: "off" | "low" | "medium" | "high";
  hitl_enabled: boolean;
  auto_reply_enabled: boolean;
  auto_reply_prompt: string;
  created_at: string;
  updated_at: string;
}

export interface ThreatDetail {
  threat_type: string;
  severity: "low" | "medium" | "high" | "critical";
  confidence: number;
  description: string;
  matched_pattern?: string;
}

export interface ThreatScanResult {
  threat_score: number;
  verdict: "allow" | "review" | "block";
  detected_threats: ThreatDetail[];
  analysis_summary: string;
}

export interface Message {
  id: string;
  agent_email: string;
  direction: "inbound" | "outbound";
  sender: string;
  recipient: string;
  subject: string;
  body_text: string;
  body_html?: string;
  thread_id: string;
  raw_message_id?: string | null;
  in_reply_to?: string;
  references?: string;
  rfc_message_id: string;
  spf_status: "pass" | "fail" | "softfail" | "neutral" | "none" | "permerror" | "temperror" | "unverified";
  dkim_status: "pass" | "fail" | "none" | "temperror" | "unverified";
  dmarc_status: "pass" | "fail" | "none" | "unverified";
  verified_domain?: string;
  delivery_error?: string | null;
  status: "delivered" | "accepted_by_relay" | "sending" | "pending_review" | "rejected" | "blocked" | "failed";
  threat_score: number;
  threat_details: string; // JSON string
  created_at: string;
}

export interface MessageAttachment {
  id: string;
  message_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  created_at: string;
}

export interface ReviewItem {
  id: string;
  message_id: string;
  agent_email: string;
  reason: string;
  threat_score: number;
  status: "pending" | "approved" | "rejected";
  reviewer_notes?: string;
  created_at: string;
  resolved_at?: string;
  message?: Message;
}

export interface Domain {
  id: string;
  domain: string;
  status: "verified" | "pending_dns";
  mx_record: string;
  mx_status: "verified" | "pending";
  spf_record: string;
  spf_status: "verified" | "pending";
  dkim_selector: string;
  dkim_record: string;
  dkim_status: "verified" | "pending";
  dmarc_record: string;
  dmarc_status: "verified" | "pending";
  created_at: string;
}

export interface SmtpConfig {
  id: string;
  host: string;
  port: string;
  username: string;
  password_configured: boolean;
  use_tls: boolean;
  use_ssl: boolean;
  from_email: string;
  enabled: boolean;
  updated_at?: string;
}

export interface ApiKeyItem {
  id: string;
  name: string;
  prefix: string;
  scope: string;
  agent_email?: string | null;
  created_at: string;
}

export interface ApiKeyCreated {
  id: string;
  name: string;
  key: string;
  prefix: string;
  scope: string;
  agent_email: string;
  created_at: string;
}

export interface Stats {
  total_agents: number;
  total_messages: number;
  inbound_count: number;
  outbound_count: number;
  pending_reviews: number;
  threats_neutralized: number;
  active_websockets: number;
}
