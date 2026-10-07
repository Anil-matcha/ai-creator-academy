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
  in_reply_to?: string;
  references?: string;
  rfc_message_id: string;
  spf_status: "pass" | "fail" | "neutral" | "none";
  dkim_status: "pass" | "fail" | "none";
  dmarc_status: "pass" | "fail" | "none";
  verified_domain?: string;
  status: "delivered" | "pending_review" | "rejected" | "blocked";
  threat_score: number;
  threat_details: string; // JSON string
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

export interface Stats {
  total_agents: number;
  total_messages: number;
  inbound_count: number;
  outbound_count: number;
  pending_reviews: number;
  threats_neutralized: number;
  active_websockets: number;
}
