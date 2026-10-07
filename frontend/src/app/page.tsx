"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  ShieldCheck,
  Mail,
  Send,
  Bot,
  Zap,
  ArrowRight,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Clock,
  Radio
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
        // Fetch recent messages across the first agent or support
        const msgs = await api.getMessages(ags[0].email, { limit: 6 });
        setRecentMessages(msgs);
      }
    } catch (err) {
      console.error("Error fetching overview data:", err);
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
    <div className="space-y-8">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl p-8 border border-white/10 bg-gradient-to-br from-indigo-950/40 via-[#0d121c] to-[#090c10] shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Open Agent Email Infrastructure v1.0</span>
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-white">
            Give Autonomous AI Agents Real, Two-Way Inboxes with Human-in-the-Loop Oversight.
          </h2>
          <p className="text-sm text-zinc-300 leading-relaxed">
            Inbound mail arrives with verified SPF/DKIM/DMARC evidence and prompt-injection screening. Outbound mail sends with RFC email threading and approval gates.
          </p>
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              href="/simulator"
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
            >
              <Zap className="w-3.5 h-3.5" />
              Simulate Inbound Email / Threat
            </Link>
            <Link
              href="/inbox"
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-zinc-200 border border-white/10 text-xs font-medium transition-all flex items-center gap-2"
            >
              <Mail className="w-3.5 h-3.5" />
              Open Agent Inboxes
            </Link>
            <Link
              href="/mcp"
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-zinc-200 border border-white/10 text-xs font-medium transition-all flex items-center gap-2"
            >
              <Bot className="w-3.5 h-3.5" />
              Connect Cursor / Claude MCP
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="glass-panel p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between text-zinc-300">
            <span className="text-xs font-medium">Active Agent Inboxes</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white font-mono">
              {stats?.total_agents ?? 0}
            </span>
            <span className="text-[11px] text-zinc-300 font-mono">@agents.local</span>
          </div>
          <div className="text-[11px] text-zinc-400 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Ready for real-time delivery
          </div>
        </div>

        {/* Metric 2 */}
        <div className="glass-panel p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between text-zinc-300">
            <span className="text-xs font-medium">Total Processed Mail</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Mail className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white font-mono">
              {stats?.total_messages ?? 0}
            </span>
            <div className="flex items-center gap-2 text-[11px] text-zinc-400">
              <span>{stats?.inbound_count ?? 0} in</span>
              <span>·</span>
              <span>{stats?.outbound_count ?? 0} out</span>
            </div>
          </div>
          <div className="text-[11px] text-zinc-400">
            RFC Message-ID & in-thread preserved
          </div>
        </div>

        {/* Metric 3 */}
        <div className="glass-panel p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between text-zinc-300">
            <span className="text-xs font-medium">Prompt Injections Neutralized</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-rose-400 font-mono">
              {stats?.threats_neutralized ?? 0}
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/20">
              Zero Leakage
            </span>
          </div>
          <div className="text-[11px] text-zinc-400">
            Hidden CSS, ChatML & Exfiltration blocked
          </div>
        </div>

        {/* Metric 4 */}
        <div className="glass-panel p-5 rounded-xl space-y-3 border-amber-500/20 bg-amber-500/[0.02]">
          <div className="flex items-center justify-between text-zinc-300">
            <span className="text-xs font-medium text-amber-300">Pending Review (HITL)</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-amber-300 font-mono">
              {stats?.pending_reviews ?? 0}
            </span>
            <Link
              href="/reviews"
              className="text-[11px] font-medium text-amber-400 hover:underline flex items-center gap-0.5"
            >
              Review Queue <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="text-[11px] text-zinc-400">
            Awaiting human approval or quarantine
          </div>
        </div>
      </div>

      {/* Main Content Grid: Recent Messages + Active Agents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Recent Traffic Stream */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h3 className="text-base font-semibold text-white tracking-tight">Recent Email Traffic</h3>
              <span className="w-2 h-2 rounded-full bg-emerald-400 live-pulse" />
            </div>
            <Link href="/inbox" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium">
              View all messages <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="glass-panel rounded-xl divide-y divide-white/5 overflow-hidden">
            {recentMessages.length === 0 ? (
              <div className="p-8 text-center text-zinc-400 text-xs">
                No recent emails recorded. Send or simulate an email to view activity.
              </div>
            ) : (
              recentMessages.map((msg) => (
                <div key={msg.id} className="p-4 hover:bg-white/[0.02] transition-colors flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3.5 min-w-0">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        msg.direction === "inbound"
                          ? msg.status === "blocked"
                            ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                            : msg.status === "pending_review"
                            ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            : "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                          : "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                      }`}
                    >
                      {msg.direction === "inbound" ? (
                        msg.status === "blocked" ? (
                          <ShieldAlert className="w-4 h-4" />
                        ) : (
                          <Mail className="w-4 h-4" />
                        )
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-zinc-200 truncate">
                          {msg.subject || "(No Subject)"}
                        </span>
                        {msg.threat_score > 0 && (
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                            Risk {Math.round(msg.threat_score * 100)}%
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-zinc-400 truncate">
                        <span>{msg.direction === "inbound" ? `From: ${msg.sender}` : `To: ${msg.recipient}`}</span>
                        <span>·</span>
                        <span className="font-mono text-zinc-300">{msg.agent_email}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full capitalize font-medium ${
                        msg.status === "delivered"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : msg.status === "pending_review"
                          ? "bg-amber-500/10 text-amber-300 border border-amber-500/20"
                          : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                      }`}
                    >
                      {msg.status.replace("_", " ")}
                    </span>
                    <span className="text-[11px] text-zinc-400 font-mono hidden sm:inline">
                      {new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Col: Configured Agent Inboxes */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-white tracking-tight">Active Inboxes</h3>
            <Link href="/agents" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">
              Manage
            </Link>
          </div>

          <div className="space-y-3">
            {agents.map((ag) => (
              <div key={ag.id} className="glass-panel p-4 rounded-xl space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                    <span className="text-xs font-semibold text-zinc-200 truncate">{ag.display_name}</span>
                  </div>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-zinc-300 border border-white/10 uppercase">
                    Scan: {ag.threat_sensitivity}
                  </span>
                </div>
                <div className="text-[11px] font-mono text-indigo-400 truncate">
                  {ag.email}
                </div>
                <div className="flex items-center justify-between text-[11px] text-zinc-400 pt-1 border-t border-white/5">
                  <span className="flex items-center gap-1">
                    <Lock className="w-3 h-3 text-zinc-300" />
                    HITL Gate: {ag.hitl_enabled ? "ON" : "OFF"}
                  </span>
                  <span>{ag.auto_reply_enabled ? "Auto-reply" : "Manual"}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Quick MCP Info Box */}
          <div className="p-4 rounded-xl border border-indigo-500/20 bg-indigo-500/[0.03] space-y-2">
            <div className="flex items-center gap-2 text-indigo-300 text-xs font-semibold">
              <Bot className="w-4 h-4" />
              <span>MCP Coding Agent Ready</span>
            </div>
            <p className="text-[11px] text-zinc-400 leading-relaxed">
              Connect Cursor or Claude Code to stream this inbox and send emails automatically.
            </p>
            <div className="bg-[#090c10] p-2 rounded-lg font-mono text-[10px] text-zinc-300 border border-white/5 flex items-center justify-between">
              <span>http://127.0.0.1:8000/mcp/rpc</span>
              <Link href="/mcp" className="text-indigo-400 hover:underline">Config</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
