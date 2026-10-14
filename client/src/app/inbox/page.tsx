"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Mail,
  Send,
  ShieldCheck,
  ShieldAlert,
  Reply,
  Forward,
  Plus,
  Bot
} from "lucide-react";
import { api } from "@/lib/api";
import { Agent, Message } from "@/lib/types";
import { Dropdown } from "@/components/Dropdown";

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
  const [handoffRecipient, setHandoffRecipient] = useState<string>("");
  const [handoffNote, setHandoffNote] = useState<string>("");
  const [sendingHandoff, setSendingHandoff] = useState<boolean>(false);
  const [handoffResult, setHandoffResult] = useState<string>("");

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
      await loadMessages();
      setSelectedMessage(reply);
    } catch (err: any) {
      alert(`Failed to send reply: ${err.message}`);
    } finally {
      setSendingReply(false);
    }
  };

  const handleHandoff = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedMessage || !handoffRecipient.trim()) return;
    try {
      setSendingHandoff(true);
      setHandoffResult("");
      const forwarded = await api.forwardMessage(selectedAgentEmail, selectedMessage.id, {
        recipient: handoffRecipient.trim(),
        note: handoffNote.trim() || undefined,
      });
      setHandoffResult(forwarded.status === "pending_review"
        ? "Handoff is waiting for outbound approval."
        : forwarded.status === "failed"
          ? `Delivery failed: ${forwarded.delivery_error || "Check the SMTP relay settings."}`
          : `Forwarded to ${forwarded.recipient}.`);
      setHandoffRecipient("");
      setHandoffNote("");
      await loadMessages();
    } catch (err) {
      setHandoffResult(err instanceof Error ? err.message : "Could not forward this message.");
    } finally {
      setSendingHandoff(false);
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

  if (agents.length === 0 && !loading) {
    return (
      <div className="card-simple p-12 text-center text-xs text-[#8b949e] space-y-3">
        <Bot className="w-8 h-8 text-[#8b949e] mx-auto" />
        <div className="text-sm font-semibold text-[#e6edf3]">No Agent Inboxes Configured</div>
        <p className="max-w-md mx-auto text-[11px]">
          Create an agent inbox to start receiving, viewing, and sending real two-way email threads.
        </p>
        <Link
          href="/agents"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#238636] hover:bg-[#2ea043] text-white text-xs font-medium"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Create Agent Inbox</span>
        </Link>
      </div>
    );
  }

  const agentDropdownOptions = agents.map((ag) => ({
    value: ag.email,
    label: `${ag.display_name}`,
    sublabel: ag.email,
  }));

  const directionOptions = [
    { value: "", label: "All Messages" },
    { value: "inbound", label: "Inbound Only" },
    { value: "outbound", label: "Outbound Only" },
  ];

  return (
    <div className="space-y-4">
      {/* Top Controls Row */}
      <div className="card-simple p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Custom Dropdowns for Agent & Filter */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="w-64">
            <Dropdown
              options={agentDropdownOptions}
              value={selectedAgentEmail}
              onChange={(val) => {
                setSelectedAgentEmail(val);
                setSelectedMessage(null);
              }}
              placeholder="Select an Agent Inbox"
            />
          </div>

          <div className="w-44">
            <Dropdown
              options={directionOptions}
              value={filterDirection}
              onChange={setFilterDirection}
            />
          </div>
        </div>

        <button
          onClick={() => setIsComposeOpen(true)}
          className="px-3 py-2 rounded bg-[#238636] hover:bg-[#2ea043] text-white text-xs font-medium flex items-center gap-1.5 transition-colors self-start sm:self-auto"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Compose Outbound</span>
        </button>
      </div>

      {/* Two-Column Client */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-[600px]">
        {/* Left: Message List */}
        <div className="lg:col-span-5 card-simple flex flex-col overflow-hidden">
          <div className="p-3 border-b border-[#30363d] flex items-center justify-between text-xs text-[#8b949e]">
            <span className="font-medium text-[#e6edf3]">
              Messages ({messages.length})
            </span>
            <button onClick={loadMessages} className="hover:text-[#e6edf3] text-[11px]">
              Refresh
            </button>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-[#30363d]">
            {messages.length === 0 ? (
              <div className="p-10 text-center text-xs text-[#8b949e]">
                No messages found for this inbox.
              </div>
            ) : (
              messages.map((msg) => {
                const isSelected = selectedMessage?.id === msg.id;
                return (
                  <div
                    key={msg.id}
                    onClick={() => setSelectedMessage(msg)}
                    className={`p-3 cursor-pointer text-xs transition-colors ${
                      isSelected
                        ? "bg-[#21262d] border-l-2 border-blue-400"
                        : "hover:bg-[#1c2128]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="font-medium text-[#e6edf3] truncate">
                        {msg.direction === "inbound" ? msg.sender : `To: ${msg.recipient}`}
                      </span>
                      <span className="text-[10px] font-mono text-[#8b949e] shrink-0">
                        {new Date(msg.created_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>

                    <div className="text-[#e6edf3] font-medium truncate mb-1">
                      {msg.subject || "(No Subject)"}
                    </div>

                    <p className="text-[11px] text-[#8b949e] line-clamp-2">
                      {msg.body_text}
                    </p>

                    <div className="flex items-center gap-1.5 mt-2">
                      <span className="text-[9px] font-mono px-1.5 py-0.2 rounded border border-[#30363d] text-[#8b949e] capitalize">
                        {msg.direction}
                      </span>
                      <span
                        className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${
                          msg.status === "delivered"
                            ? "bg-[#238636]/10 text-[#2ea043] border-[#2ea043]/30"
                            : msg.status === "pending_review"
                            ? "bg-[#9e6a03]/10 text-[#d29922] border-[#d29922]/30"
                            : "bg-[#da3633]/10 text-[#f85149] border-[#f85149]/30"
                        }`}
                      >
                        {msg.status.replace("_", " ")}
                      </span>
                      {msg.spf_status === "pass" && msg.dkim_status === "pass" && msg.dmarc_status === "pass" && (
                        <span className="text-[9px] font-mono text-[#2ea043] flex items-center gap-0.5 ml-auto">
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

        {/* Right: Message Detail & Thread */}
        <div className="lg:col-span-7 card-simple flex flex-col overflow-hidden">
          {selectedMessage ? (
            <div className="flex-1 flex flex-col h-full">
              {/* Header */}
              <div className="p-4 border-b border-[#30363d] space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-sm font-semibold text-[#e6edf3]">
                      {selectedMessage.subject || "(No Subject)"}
                    </h3>
                    <div className="text-[11px] text-[#8b949e] font-mono mt-0.5">
                      Thread: {selectedMessage.thread_id} ·{" "}
                      {new Date(selectedMessage.created_at).toLocaleString()}
                    </div>
                  </div>

                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded border capitalize ${
                      selectedMessage.status === "delivered"
                        ? "bg-[#238636]/10 text-[#2ea043] border-[#2ea043]/30"
                        : selectedMessage.status === "pending_review"
                        ? "bg-[#9e6a03]/10 text-[#d29922] border-[#d29922]/30"
                        : "bg-[#da3633]/10 text-[#f85149] border-[#f85149]/30"
                    }`}
                  >
                    {selectedMessage.status.replace("_", " ")}
                  </span>
                </div>

                <div className="bg-[#0d1117] p-2.5 rounded border border-[#30363d] space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-[#8b949e]">From:</span>
                    <span className="font-mono text-[#e6edf3]">{selectedMessage.sender}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#8b949e]">To:</span>
                    <span className="font-mono text-blue-400">{selectedMessage.recipient}</span>
                  </div>
                  <div className="flex justify-between text-[11px] text-[#8b949e]">
                    <span>Message-ID:</span>
                    <span className="font-mono truncate max-w-xs">{selectedMessage.rfc_message_id}</span>
                  </div>
                </div>

                {/* Authentication Tags */}
                <div className="flex items-center gap-2 text-[10px] font-mono">
                  <span className="px-2 py-0.5 rounded border border-[#30363d] text-[#8b949e]">
                    SPF: <strong className={selectedMessage.spf_status === "pass" ? "text-[#2ea043]" : "text-[#f85149]"}>{selectedMessage.spf_status.toUpperCase()}</strong>
                  </span>
                  <span className="px-2 py-0.5 rounded border border-[#30363d] text-[#8b949e]">
                    DKIM: <strong className={selectedMessage.dkim_status === "pass" ? "text-[#2ea043]" : "text-[#f85149]"}>{selectedMessage.dkim_status.toUpperCase()}</strong>
                  </span>
                  <span className="px-2 py-0.5 rounded border border-[#30363d] text-[#8b949e]">
                    DMARC: <strong className={selectedMessage.dmarc_status === "pass" ? "text-[#2ea043]" : "text-[#f85149]"}>{selectedMessage.dmarc_status.toUpperCase()}</strong>
                  </span>
                </div>
              </div>

              {/* Message Body */}
              <div className="p-4 flex-1 overflow-y-auto text-xs text-[#e6edf3] whitespace-pre-wrap leading-relaxed font-sans">
                {selectedMessage.body_text}
                {selectedMessage.delivery_error && (
                  <div className="mt-4 rounded border border-[#f85149]/30 bg-[#f85149]/10 p-3 text-[#f85149]">
                    Delivery failed: {selectedMessage.delivery_error}
                  </div>
                )}
              </div>

              <form onSubmit={handleHandoff} className="p-3 border-t border-[#30363d] bg-[#0d1117] space-y-2">
                <div className="text-[11px] text-[#e6edf3] flex items-center gap-1.5">
                  <Forward className="w-3 h-3 text-amber-400" /> Hand off to a person
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <input type="email" required value={handoffRecipient} onChange={(e) => setHandoffRecipient(e.target.value)} placeholder="Teammate email address" className="w-full bg-[#161b22] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] placeholder-[#8b949e]" />
                  <input type="text" value={handoffNote} onChange={(e) => setHandoffNote(e.target.value)} placeholder="Context for your teammate (optional)" className="w-full bg-[#161b22] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] placeholder-[#8b949e]" />
                </div>
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[10px] text-[#8b949e]">Forwards the original email and your context. Agent approval settings still apply.</p>
                  <button type="submit" disabled={sendingHandoff || !handoffRecipient.trim()} className="shrink-0 px-3 py-1.5 rounded border border-[#30363d] bg-[#21262d] hover:bg-[#30363d] disabled:opacity-50 text-[#e6edf3] text-xs flex items-center gap-1.5">
                    <Forward className="w-3 h-3" /> {sendingHandoff ? "Forwarding…" : "Forward"}
                  </button>
                </div>
                {handoffResult && <p className="text-[11px] text-[#d29922]">{handoffResult}</p>}
              </form>

              {/* In-Thread Reply */}
              <div className="p-3 border-t border-[#30363d] bg-[#161b22] space-y-2">
                <div className="text-[11px] text-[#8b949e] flex items-center justify-between">
                  <span className="flex items-center gap-1 text-[#e6edf3]">
                    <Reply className="w-3 h-3 text-blue-400" /> Reply in-thread
                  </span>
                  <span className="font-mono">
                    To: {selectedMessage.direction === "inbound" ? selectedMessage.sender : selectedMessage.recipient}
                  </span>
                </div>
                <textarea
                  rows={3}
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Type in-thread response..."
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2.5 text-xs text-[#e6edf3] placeholder-[#8b949e] focus:outline-none focus:border-zinc-500 resize-none"
                />
                <div className="flex justify-end">
                  <button
                    onClick={handleSendReply}
                    disabled={sendingReply || !replyText.trim()}
                    className="px-3 py-1.5 rounded bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white text-xs font-medium flex items-center gap-1.5 transition-colors"
                  >
                    <Send className="w-3 h-3" />
                    <span>{sendingReply ? "Sending..." : "Send Reply"}</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-xs text-[#8b949e]">
              <Mail className="w-8 h-8 text-[#8b949e] mb-2" />
              <div>Select an email from the left list to read.</div>
            </div>
          )}
        </div>
      </div>

      {/* Compose Outbound Modal */}
      {isComposeOpen && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg w-full max-w-lg p-5 space-y-3 shadow-xl">
            <div className="flex items-center justify-between pb-2 border-b border-[#30363d]">
              <h4 className="text-xs font-semibold text-[#e6edf3]">Compose Outbound Email</h4>
              <button
                onClick={() => setIsComposeOpen(false)}
                className="text-[#8b949e] hover:text-[#e6edf3] text-xs"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleComposeSend} className="space-y-3 text-xs">
              <div>
                <label className="text-[#8b949e] block mb-1">From Agent</label>
                <input
                  type="text"
                  disabled
                  value={selectedAgentEmail}
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#8b949e] font-mono"
                />
              </div>

              <div>
                <label className="text-[#8b949e] block mb-1">Recipient</label>
                <input
                  type="email"
                  required
                  placeholder="recipient@example.com"
                  value={composeRecipient}
                  onChange={(e) => setComposeRecipient(e.target.value)}
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] focus:outline-none focus:border-zinc-500"
                />
              </div>

              <div>
                <label className="text-[#8b949e] block mb-1">Subject</label>
                <input
                  type="text"
                  required
                  placeholder="Subject"
                  value={composeSubject}
                  onChange={(e) => setComposeSubject(e.target.value)}
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] focus:outline-none focus:border-zinc-500"
                />
              </div>

              <div>
                <label className="text-[#8b949e] block mb-1">Body</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Message body..."
                  value={composeBody}
                  onChange={(e) => setComposeBody(e.target.value)}
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] focus:outline-none focus:border-zinc-500 resize-none font-sans"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsComposeOpen(false)}
                  className="px-3 py-1.5 rounded border border-[#30363d] text-[#8b949e] hover:text-[#e6edf3]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sendingCompose}
                  className="px-3 py-1.5 rounded bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white font-medium"
                >
                  {sendingCompose ? "Sending..." : "Send"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
