"use client";

import { useEffect, useState } from "react";
import {
  Mail,
  Send,
  ShieldCheck,
  ShieldAlert,
  Reply,
  CheckCircle2,
  XCircle,
  Clock,
  Filter,
  Plus,
  ArrowRight,
  Bot,
  Hash,
  AlertCircle
} from "lucide-react";
import { api } from "@/lib/api";
import { Agent, Message } from "@/lib/types";

export default function InboxPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentEmail, setSelectedAgentEmail] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [filterDirection, setFilterDirection] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  // In-Thread Reply Form
  const [replyText, setReplyText] = useState<string>("");
  const [sendingReply, setSendingReply] = useState<boolean>(false);

  // New Compose Outbound Modal
  const [isComposeOpen, setIsComposeOpen] = useState<boolean>(false);
  const [composeRecipient, setComposeRecipient] = useState<string>("");
  const [composeSubject, setComposeSubject] = useState<string>("");
  const [composeBody, setComposeBody] = useState<string>("");
  const [sendingCompose, setSendingCompose] = useState<boolean>(false);

  // Load Agents
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const ags = await api.getAgents();
        setAgents(ags);
        if (ags.length > 0) {
          setSelectedAgentEmail(ags[0].email);
        }
      } catch (err) {
        console.error("Failed to load agents:", err);
      }
    };
    fetchAgents();
  }, []);

  // Load Messages for Selected Agent
  const loadMessages = async () => {
    if (!selectedAgentEmail) return;
    try {
      setLoading(true);
      const msgs = await api.getMessages(selectedAgentEmail, {
        direction: filterDirection || undefined,
      });
      setMessages(msgs);
      if (msgs.length > 0 && !selectedMessage) {
        setSelectedMessage(msgs[0]);
      } else if (msgs.length === 0) {
        setSelectedMessage(null);
      }
    } catch (err) {
      console.error("Failed to fetch messages:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMessages();
  }, [selectedAgentEmail, filterDirection]);

  // Handle Send Reply
  const handleSendReply = async () => {
    if (!selectedMessage || !replyText.trim()) return;
    try {
      setSendingReply(true);
      const reply = await api.replyMessage(selectedAgentEmail, selectedMessage.id, {
        body_text: replyText,
      });
      setReplyText("");
      // Refresh messages
      await loadMessages();
      setSelectedMessage(reply);
    } catch (err: any) {
      alert(`Failed to send reply: ${err.message}`);
    } finally {
      setSendingReply(false);
    }
  };

  // Handle Fresh Outbound Compose
  const handleComposeSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!composeRecipient || !composeSubject || !composeBody) return;
    try {
      setSendingCompose(true);
      const msg = await api.sendMessage(selectedAgentEmail, {
        recipient: composeRecipient,
        subject: composeSubject,
        body_text: composeBody,
      });
      setIsComposeOpen(false);
      setComposeRecipient("");
      setComposeSubject("");
      setComposeBody("");
      await loadMessages();
      setSelectedMessage(msg);
    } catch (err: any) {
      alert(`Failed to send email: ${err.message}`);
    } finally {
      setSendingCompose(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <label className="text-[10px] uppercase font-bold text-zinc-400 tracking-wider">Active Inbox</label>
            <select
              value={selectedAgentEmail}
              onChange={(e) => {
                setSelectedAgentEmail(e.target.value);
                setSelectedMessage(null);
              }}
              className="block bg-[#090c10] border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white font-mono focus:border-indigo-500 focus:outline-none"
            >
              {agents.map((ag) => (
                <option key={ag.id} value={ag.email}>
                  {ag.display_name} ({ag.email})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Direction Filter & Compose Button */}
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-[#090c10] rounded-lg p-1 border border-white/10 text-xs">
            <button
              onClick={() => setFilterDirection("")}
              className={`px-2.5 py-1 rounded-md transition-all ${
                filterDirection === "" ? "bg-indigo-600 text-white font-medium" : "text-zinc-400 hover:text-white"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterDirection("inbound")}
              className={`px-2.5 py-1 rounded-md transition-all ${
                filterDirection === "inbound" ? "bg-indigo-600 text-white font-medium" : "text-zinc-400 hover:text-white"
              }`}
            >
              Inbound
            </button>
            <button
              onClick={() => setFilterDirection("outbound")}
              className={`px-2.5 py-1 rounded-md transition-all ${
                filterDirection === "outbound" ? "bg-indigo-600 text-white font-medium" : "text-zinc-400 hover:text-white"
              }`}
            >
              Outbound
            </button>
          </div>

          <button
            onClick={() => setIsComposeOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Compose Outbound</span>
          </button>
        </div>
      </div>

      {/* Two-Column Email Client */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[640px]">
        {/* Left Column: Email Thread List */}
        <div className="lg:col-span-5 glass-panel rounded-2xl overflow-hidden flex flex-col">
          <div className="p-3.5 border-b border-white/5 flex items-center justify-between text-xs text-zinc-300">
            <span className="font-semibold text-white">Threads & Messages ({messages.length})</span>
            <button onClick={loadMessages} className="text-zinc-400 hover:text-white text-[11px]">
              Refresh
            </button>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-white/5">
            {messages.length === 0 ? (
              <div className="p-12 text-center text-zinc-400 text-xs">
                No messages found for this inbox.
              </div>
            ) : (
              messages.map((msg) => {
                const isSelected = selectedMessage?.id === msg.id;
                return (
                  <div
                    key={msg.id}
                    onClick={() => setSelectedMessage(msg)}
                    className={`p-4 cursor-pointer transition-all ${
                      isSelected
                        ? "bg-indigo-600/15 border-l-4 border-indigo-500"
                        : "hover:bg-white/[0.02]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-xs font-semibold text-zinc-200 truncate">
                        {msg.direction === "inbound" ? msg.sender : `To: ${msg.recipient}`}
                      </span>
                      <span className="text-[10px] font-mono text-zinc-300 shrink-0">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>

                    <div className="text-xs font-medium text-white truncate mb-1">
                      {msg.subject || "(No Subject)"}
                    </div>

                    <p className="text-[11px] text-zinc-400 line-clamp-2 leading-relaxed">
                      {msg.body_text}
                    </p>

                    <div className="flex items-center gap-2 mt-2 pt-1">
                      <span
                        className={`text-[9px] font-mono px-1.5 py-0.5 rounded capitalize ${
                          msg.direction === "inbound"
                            ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20"
                            : "bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                        }`}
                      >
                        {msg.direction}
                      </span>

                      <span
                        className={`text-[9px] font-mono px-1.5 py-0.5 rounded capitalize ${
                          msg.status === "delivered"
                            ? "bg-emerald-500/10 text-emerald-400"
                            : msg.status === "pending_review"
                            ? "bg-amber-500/10 text-amber-300"
                            : "bg-rose-500/10 text-rose-400"
                        }`}
                      >
                        {msg.status.replace("_", " ")}
                      </span>

                      {msg.threat_score > 0 && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">
                          Threat {Math.round(msg.threat_score * 100)}%
                        </span>
                      )}

                      {msg.spf_status === "pass" && msg.dkim_status === "pass" && (
                        <span className="text-[9px] font-mono text-emerald-400 flex items-center gap-0.5 ml-auto">
                          <ShieldCheck className="w-3 h-3" /> VERIFIED
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Message Detail & Thread View */}
        <div className="lg:col-span-7 glass-panel rounded-2xl flex flex-col overflow-hidden">
          {selectedMessage ? (
            <div className="flex-1 flex flex-col h-full">
              {/* Message Header */}
              <div className="p-6 border-b border-white/5 space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-bold text-white tracking-tight">
                      {selectedMessage.subject || "(No Subject)"}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-zinc-400 mt-1 font-mono">
                      <span>Thread: {selectedMessage.thread_id}</span>
                      <span>·</span>
                      <span>{new Date(selectedMessage.created_at).toLocaleString()}</span>
                    </div>
                  </div>

                  <span
                    className={`text-[10px] font-mono px-2.5 py-1 rounded-full uppercase font-bold tracking-wider ${
                      selectedMessage.status === "delivered"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : selectedMessage.status === "pending_review"
                        ? "bg-amber-500/10 text-amber-300 border border-amber-500/20"
                        : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                    }`}
                  >
                    {selectedMessage.status.replace("_", " ")}
                  </span>
                </div>

                {/* Sender & Recipient addresses */}
                <div className="p-3 rounded-xl bg-[#090c10] border border-white/5 space-y-1.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-400">From:</span>
                    <span className="font-mono text-zinc-200">{selectedMessage.sender}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-400">To:</span>
                    <span className="font-mono text-indigo-400">{selectedMessage.recipient}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-zinc-300">
                    <span>RFC Message-ID:</span>
                    <span className="font-mono truncate max-w-sm">{selectedMessage.rfc_message_id}</span>
                  </div>
                </div>

                {/* Authentication & Security Evidence Strip */}
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded bg-white/[0.03] border border-white/10 text-[11px] font-mono">
                    <span className="text-zinc-400">SPF:</span>
                    <span className={selectedMessage.spf_status === "pass" ? "text-emerald-400" : "text-rose-400"}>
                      {selectedMessage.spf_status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded bg-white/[0.03] border border-white/10 text-[11px] font-mono">
                    <span className="text-zinc-400">DKIM:</span>
                    <span className={selectedMessage.dkim_status === "pass" ? "text-emerald-400" : "text-rose-400"}>
                      {selectedMessage.dkim_status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded bg-white/[0.03] border border-white/10 text-[11px] font-mono">
                    <span className="text-zinc-400">DMARC:</span>
                    <span className={selectedMessage.dmarc_status === "pass" ? "text-emerald-400" : "text-rose-400"}>
                      {selectedMessage.dmarc_status.toUpperCase()}
                    </span>
                  </div>
                  {selectedMessage.verified_domain && (
                    <div className="flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-mono text-emerald-300">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>Aligned Domain: {selectedMessage.verified_domain}</span>
                    </div>
                  )}
                </div>

                {/* Threat alert if flagged */}
                {selectedMessage.threat_score > 0 && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 flex items-start gap-2.5">
                    <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                    <div>
                      <div className="font-semibold">Security Alert: Threat Score {Math.round(selectedMessage.threat_score * 100)}%</div>
                      <div className="text-[11px] text-rose-300/80 font-mono mt-0.5">
                        Details: {selectedMessage.threat_details}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Email Content Body */}
              <div className="p-6 flex-1 overflow-y-auto">
                <div className="prose prose-invert max-w-none text-sm leading-relaxed whitespace-pre-wrap text-zinc-200">
                  {selectedMessage.body_text}
                </div>
              </div>

              {/* In-Thread Reply Form */}
              <div className="p-4 border-t border-white/5 bg-[#0a0d14]/60">
                <div className="flex items-center justify-between text-xs text-zinc-400 mb-2">
                  <span className="flex items-center gap-1 font-medium text-zinc-300">
                    <Reply className="w-3.5 h-3.5 text-indigo-400" /> Reply In-Thread (preserves Message-ID & In-Reply-To)
                  </span>
                  <span className="font-mono text-[10px] text-zinc-300">
                    To: {selectedMessage.direction === "inbound" ? selectedMessage.sender : selectedMessage.recipient}
                  </span>
                </div>
                <div className="space-y-3">
                  <textarea
                    rows={3}
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Compose autonomous agent reply..."
                    className="w-full bg-[#090c10] border border-white/10 rounded-xl p-3 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none font-sans"
                  />
                  <div className="flex justify-end">
                    <button
                      onClick={handleSendReply}
                      disabled={sendingReply || !replyText.trim()}
                      className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-2 shadow-md shadow-indigo-600/30 transition-all"
                    >
                      <Send className="w-3.5 h-3.5" />
                      <span>{sendingReply ? "Dispatching..." : "Send Reply"}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center text-zinc-400">
              <Mail className="w-12 h-12 text-zinc-600 mb-3" />
              <p className="text-sm font-medium text-zinc-300">Select an email to view full RFC thread</p>
              <p className="text-xs text-zinc-500 mt-1">
                Reads both inbound mail from customers and outbound replies from AI agents.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Compose Outbound Modal */}
      {isComposeOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0d121c] border border-white/10 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <Send className="w-4 h-4 text-indigo-400" />
                Compose Outbound Email
              </h4>
              <button
                onClick={() => setIsComposeOpen(false)}
                className="text-zinc-400 hover:text-white text-xs"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleComposeSend} className="space-y-3">
              <div>
                <label className="text-xs text-zinc-400 block mb-1">From Agent</label>
                <input
                  type="text"
                  disabled
                  value={selectedAgentEmail}
                  className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-zinc-400 font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-400 block mb-1">Recipient Email</label>
                <input
                  type="email"
                  required
                  placeholder="recipient@example.com"
                  value={composeRecipient}
                  onChange={(e) => setComposeRecipient(e.target.value)}
                  className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-400 block mb-1">Subject</label>
                <input
                  type="text"
                  required
                  placeholder="Subject line"
                  value={composeSubject}
                  onChange={(e) => setComposeSubject(e.target.value)}
                  className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-400 block mb-1">Body</label>
                <textarea
                  rows={5}
                  required
                  placeholder="Type outbound message content..."
                  value={composeBody}
                  onChange={(e) => setComposeBody(e.target.value)}
                  className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500 resize-none font-sans"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsComposeOpen(false)}
                  className="px-3 py-1.5 rounded-lg border border-white/10 text-zinc-400 hover:text-white text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sendingCompose}
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-md shadow-indigo-600/30"
                >
                  {sendingCompose ? "Sending..." : "Dispatch Email"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
