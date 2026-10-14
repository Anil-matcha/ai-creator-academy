"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Mail,
  Send,
  ShieldAlert,
  Bot,
  ArrowRight,
  Plus
} from "lucide-react";
import { api } from "@/lib/api";
import { Stats, Message, Agent } from "@/lib/types";

export default function OverviewPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [recentMessages, setRecentMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      const s = await api.getStats();
      setStats(s);

      const ags = await api.getAgents();
      setAgents(ags);

      if (ags.length > 0) {
        const msgs = await api.getMessages(ags[0].email, { limit: 10 });
        setRecentMessages(msgs);
      } else {
        setRecentMessages([]);
      }
    } catch {
      // quiet fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card-simple p-4 space-y-1">
          <div className="text-xs text-[#8b949e]">Active Agents</div>
          <div className="text-2xl font-semibold text-[#e6edf3] font-mono">
            {stats?.total_agents ?? 0}
          </div>
          <div className="text-[11px] text-[#8b949e]">Configured inboxes</div>
        </div>

        <div className="card-simple p-4 space-y-1">
          <div className="text-xs text-[#8b949e]">Total Messages</div>
          <div className="text-2xl font-semibold text-[#e6edf3] font-mono">
            {stats?.total_messages ?? 0}
          </div>
          <div className="text-[11px] text-[#8b949e]">
            {stats?.inbound_count ?? 0} in · {stats?.outbound_count ?? 0} out
          </div>
        </div>

        <div className="card-simple p-4 space-y-1">
          <div className="text-xs text-[#8b949e]">Pending Reviews</div>
          <div className="text-2xl font-semibold text-[#d29922] font-mono">
            {stats?.pending_reviews ?? 0}
          </div>
          <div className="text-[11px] text-[#8b949e]">Awaiting human decision</div>
        </div>

        <div className="card-simple p-4 space-y-1">
          <div className="text-xs text-[#8b949e]">Threats Intercepted</div>
          <div className="text-2xl font-semibold text-[#f85149] font-mono">
            {stats?.threats_neutralized ?? 0}
          </div>
          <div className="text-[11px] text-[#8b949e]">Prompt injections blocked</div>
        </div>
      </div>

      {/* Main Grid: Messages + Inboxes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Messages Column */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-[#e6edf3] uppercase tracking-wider">
              Recent Email Activity
            </h2>
            <Link
              href="/inbox"
              className="text-xs text-blue-400 hover:underline flex items-center gap-1"
            >
              Open Inbox <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="card-simple divide-y divide-[#30363d] overflow-hidden">
            {recentMessages.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#8b949e] space-y-2">
                <div>No emails found yet.</div>
                <div className="text-[11px]">
                  Use the Simulator to test inbound email or create an agent inbox to get started.
                </div>
                <div className="pt-2 flex justify-center gap-2">
                  <Link
                    href="/agents"
                    className="px-3 py-1.5 rounded bg-[#238636] hover:bg-[#2ea043] text-white text-xs font-medium"
                  >
                    Create Agent Inbox
                  </Link>
                  <Link
                    href="/simulator"
                    className="px-3 py-1.5 rounded border border-[#30363d] bg-[#21262d] text-xs text-[#e6edf3]"
                  >
                    Test Inbound
                  </Link>
                </div>
              </div>
            ) : (
              recentMessages.map((msg) => (
                <div
                  key={msg.id}
                  className="p-3 hover:bg-[#1c2128] transition-colors flex items-center justify-between gap-3 text-xs"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-[#8b949e] shrink-0">
                      {msg.direction === "inbound" ? (
                        <Mail className="w-4 h-4 text-cyan-400" />
                      ) : (
                        <Send className="w-4 h-4 text-blue-400" />
                      )}
                    </span>
                    <div className="min-w-0">
                      <div className="font-medium text-[#e6edf3] truncate">
                        {msg.subject || "(No Subject)"}
                      </div>
                      <div className="text-[11px] text-[#8b949e] truncate">
                        {msg.direction === "inbound" ? msg.sender : msg.recipient} → {msg.agent_email}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                        msg.status === "delivered" || msg.status === "accepted_by_relay"
                          ? "bg-[#238636]/10 text-[#2ea043] border-[#2ea043]/30"
                          : msg.status === "pending_review" || msg.status === "sending" || msg.status === "delivery_unknown"
                          ? "bg-[#9e6a03]/10 text-[#d29922] border-[#d29922]/30"
                          : "bg-[#da3633]/10 text-[#f85149] border-[#f85149]/30"
                      }`}
                    >
                      {msg.status.replace("_", " ")}
                    </span>
                    <span className="text-[10px] font-mono text-[#8b949e]">
                      {new Date(msg.created_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Agents Column */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-[#e6edf3] uppercase tracking-wider">
              Agent Inboxes
            </h2>
            <Link
              href="/agents"
              className="text-xs text-blue-400 hover:underline flex items-center gap-1"
            >
              Manage <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="card-simple divide-y divide-[#30363d] overflow-hidden">
            {agents.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#8b949e] space-y-2">
                <div>No inboxes configured.</div>
                <Link
                  href="/agents"
                  className="inline-flex items-center gap-1 text-xs text-blue-400 hover:underline"
                >
                  <Plus className="w-3 h-3" /> Add first agent
                </Link>
              </div>
            ) : (
              agents.map((ag) => (
                <div key={ag.id} className="p-3 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-[#e6edf3]">{ag.display_name}</span>
                    <span className="text-[10px] font-mono text-[#8b949e] uppercase">
                      {ag.threat_sensitivity} scan
                    </span>
                  </div>
                  <div className="font-mono text-[11px] text-blue-400 truncate">
                    {ag.email}
                  </div>
                  <div className="text-[10px] text-[#8b949e] flex items-center justify-between pt-1">
                    <span>HITL: {ag.hitl_enabled ? "Enabled" : "Off"}</span>
                    <span>Auto-reply: {ag.auto_reply_enabled ? "On" : "Off"}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Quick MCP Info Box */}
          <div className="card-simple p-3 text-xs space-y-1.5">
            <div className="font-semibold text-[#e6edf3] flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5 text-blue-400" />
              <span>MCP Server Endpoint</span>
            </div>
            <p className="text-[11px] text-[#8b949e]">
              Connect Cursor or Claude Code to let agents interact with inboxes via MCP tools.
            </p>
            <div className="bg-[#0d1117] p-2 rounded border border-[#30363d] font-mono text-[10px] text-[#8b949e] truncate">
              http://127.0.0.1:8000/mcp/rpc
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
