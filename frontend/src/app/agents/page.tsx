"use client";

import { useEffect, useState } from "react";
import {
  Bot,
  Plus,
  Shield,
  ShieldAlert,
  Radio,
  Trash2,
  Save,
  CheckCircle2,
  Lock,
  MessageSquare,
  Sparkles
} from "lucide-react";
import { api } from "@/lib/api";
import { Agent } from "@/lib/types";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Create Agent Modal
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [newEmailSlug, setNewEmailSlug] = useState<string>("");
  const [newDisplayName, setNewDisplayName] = useState<string>("");
  const [newDescription, setNewDescription] = useState<string>("");
  const [newSensitivity, setNewSensitivity] = useState<string>("medium");
  const [newHitl, setNewHitl] = useState<boolean>(true);
  const [creating, setCreating] = useState<boolean>(false);

  // Edit State
  const [editSensitivity, setEditSensitivity] = useState<string>("medium");
  const [editHitl, setEditHitl] = useState<boolean>(true);
  const [editAutoReply, setEditAutoReply] = useState<boolean>(false);
  const [editPrompt, setEditPrompt] = useState<string>("");
  const [saving, setSaving] = useState<boolean>(false);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const ags = await api.getAgents();
      setAgents(ags);
      if (ags.length > 0) {
        selectAgent(ags[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectAgent = (ag: Agent) => {
    setSelectedAgent(ag);
    setEditSensitivity(ag.threat_sensitivity);
    setEditHitl(ag.hitl_enabled);
    setEditAutoReply(ag.auto_reply_enabled);
    setEditPrompt(ag.auto_reply_prompt || "");
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmailSlug.trim() || !newDisplayName.trim()) return;
    try {
      setCreating(true);
      const fullEmail = newEmailSlug.includes("@") ? newEmailSlug : `${newEmailSlug}@agents.local`;
      const created = await api.createAgent({
        email: fullEmail,
        display_name: newDisplayName,
        description: newDescription,
        threat_sensitivity: newSensitivity as any,
        hitl_enabled: newHitl,
      });
      setIsCreateOpen(false);
      setNewEmailSlug("");
      setNewDisplayName("");
      setNewDescription("");
      await fetchAgents();
      selectAgent(created);
    } catch (err: any) {
      alert(`Failed to create agent: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const handleSaveConfig = async () => {
    if (!selectedAgent) return;
    try {
      setSaving(true);
      const updated = await api.updateAgent(selectedAgent.email, {
        threat_sensitivity: editSensitivity as any,
        hitl_enabled: editHitl,
        auto_reply_enabled: editAutoReply,
        auto_reply_prompt: editPrompt,
      });
      await fetchAgents();
      selectAgent(updated);
      alert("Agent security and automation posture updated successfully!");
    } catch (err: any) {
      alert(`Save error: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (email: string) => {
    if (!confirm(`Are you sure you want to delete agent inbox ${email}?`)) return;
    try {
      await api.deleteAgent(email);
      await fetchAgents();
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <Bot className="w-5 h-5 text-indigo-400" />
            Agent Inboxes & Security Posture
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Manage distinct agent email addresses, threat sensitivity thresholds, and autonomous auto-reply policies.
          </p>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md shadow-indigo-600/30 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Provision New Agent Inbox</span>
        </button>
      </div>

      {/* Main Grid: Agent List + Settings Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[580px]">
        {/* Left Column: Agents List */}
        <div className="lg:col-span-5 glass-panel rounded-2xl flex flex-col overflow-hidden">
          <div className="p-3.5 border-b border-white/5 flex items-center justify-between text-xs text-zinc-400">
            <span className="font-semibold text-white">Configured Inboxes ({agents.length})</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-white/5">
            {agents.map((ag) => {
              const isSelected = selectedAgent?.id === ag.id;
              return (
                <div
                  key={ag.id}
                  onClick={() => selectAgent(ag)}
                  className={`p-4 cursor-pointer transition-all ${
                    isSelected ? "bg-indigo-600/15 border-l-4 border-indigo-500" : "hover:bg-white/[0.02]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-zinc-200">{ag.display_name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-zinc-300 uppercase">
                      {ag.threat_sensitivity} scan
                    </span>
                  </div>

                  <div className="text-xs font-mono text-indigo-400 mb-1">{ag.email}</div>
                  <p className="text-[11px] text-zinc-400 line-clamp-1">{ag.description}</p>

                  <div className="flex items-center justify-between text-[10px] text-zinc-400 mt-2 pt-1 border-t border-white/5">
                    <span>HITL Gate: {ag.hitl_enabled ? "Enabled" : "Disabled"}</span>
                    <span>{ag.auto_reply_enabled ? "Auto-Reply ON" : "Auto-Reply OFF"}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Posture Configuration Editor */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 flex flex-col justify-between">
          {selectedAgent ? (
            <div className="space-y-6">
              <div className="flex items-start justify-between pb-4 border-b border-white/5">
                <div>
                  <h3 className="text-lg font-bold text-white tracking-tight">{selectedAgent.display_name}</h3>
                  <div className="text-xs font-mono text-indigo-400 mt-0.5">{selectedAgent.email}</div>
                  <p className="text-xs text-zinc-400 mt-1">{selectedAgent.description}</p>
                </div>

                <button
                  onClick={() => handleDelete(selectedAgent.email)}
                  className="p-2 rounded-lg border border-rose-500/20 text-rose-400 hover:bg-rose-500/10 transition-all text-xs"
                  title="Delete Inbox"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {/* Threat Scan Sensitivity */}
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  Inbound Threat Scan Sensitivity
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {["off", "low", "medium", "high"].map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setEditSensitivity(level)}
                      className={`p-2.5 rounded-xl border text-xs font-semibold capitalize transition-all ${
                        editSensitivity === level
                          ? "bg-indigo-600 text-white border-indigo-500 shadow-sm shadow-indigo-600/30"
                          : "bg-[#090c10] border-white/10 text-zinc-400 hover:text-white"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
                <p className="text-[11px] text-zinc-400">
                  {editSensitivity === "off" && "No threat scanning. All inbound emails delivered directly."}
                  {editSensitivity === "low" && "Flags only high-confidence attacks (>0.70 score) for review."}
                  {editSensitivity === "medium" && "Default. Standard heuristic detection (>0.50 score held in HITL)."}
                  {editSensitivity === "high" && "Strict posture. Flags any suspicious syntax (>0.30 score) into review queue."}
                </p>
              </div>

              {/* Human-in-the-Loop Toggle */}
              <div className="p-4 rounded-xl bg-[#090c10] border border-white/5 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-white flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-indigo-400" />
                    Human-in-the-Loop (HITL) Approval Gate
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-0.5">
                    Holds flagged inbound and sensitive outbound emails in the review queue.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={editHitl}
                  onChange={(e) => setEditHitl(e.target.checked)}
                  className="w-5 h-5 accent-indigo-600 cursor-pointer"
                />
              </div>

              {/* Autonomous Auto-Reply Toggle & Prompt */}
              <div className="space-y-3 p-4 rounded-xl bg-[#090c10] border border-white/5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs font-semibold text-white flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      Autonomous Auto-Reply
                    </div>
                    <p className="text-[11px] text-zinc-400 mt-0.5">
                      Agent automatically composes and dispatches in-thread replies to verified, clean emails.
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={editAutoReply}
                    onChange={(e) => setEditAutoReply(e.target.checked)}
                    className="w-5 h-5 accent-indigo-600 cursor-pointer"
                  />
                </div>

                {editAutoReply && (
                  <div className="pt-2 border-t border-white/5 space-y-1">
                    <label className="text-[11px] text-zinc-400 font-medium">Agent System Prompt Directive</label>
                    <textarea
                      rows={3}
                      value={editPrompt}
                      onChange={(e) => setEditPrompt(e.target.value)}
                      className="w-full bg-[#0d121c] border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                    />
                  </div>
                )}
              </div>

              {/* Save Button */}
              <div className="pt-4 flex justify-end">
                <button
                  onClick={handleSaveConfig}
                  disabled={saving}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all"
                >
                  <Save className="w-4 h-4" />
                  <span>{saving ? "Saving Posture..." : "Save Configuration"}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-12 text-zinc-500">
              <Bot className="w-12 h-12 text-zinc-700 mb-3" />
              <p className="text-xs text-zinc-400">Select an agent inbox to configure its security posture</p>
            </div>
          )}
        </div>
      </div>

      {/* Provision Agent Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0d121c] border border-white/10 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <Bot className="w-4 h-4 text-indigo-400" />
                Provision Agent Inbox
              </h4>
              <button onClick={() => setIsCreateOpen(false)} className="text-zinc-400 hover:text-white text-xs">
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateAgent} className="space-y-3">
              <div>
                <label className="text-xs text-zinc-400 block mb-1">Email Slug or Address</label>
                <div className="flex items-center">
                  <input
                    type="text"
                    required
                    placeholder="e.g. triage or billing"
                    value={newEmailSlug}
                    onChange={(e) => setNewEmailSlug(e.target.value)}
                    className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                  {!newEmailSlug.includes("@") && (
                    <span className="text-xs font-mono text-zinc-500 pl-2">@agents.local</span>
                  )}
                </div>
              </div>

              <div>
                <label className="text-xs text-zinc-400 block mb-1">Display Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Triage Operations Bot"
                  value={newDisplayName}
                  onChange={(e) => setNewDisplayName(e.target.value)}
                  className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-400 block mb-1">Description</label>
                <textarea
                  rows={2}
                  placeholder="Purpose of this autonomous inbox..."
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-400 block mb-1">Threat Sensitivity</label>
                <select
                  value={newSensitivity}
                  onChange={(e) => setNewSensitivity(e.target.value)}
                  className="w-full bg-[#090c10] border border-white/10 rounded-lg p-2 text-xs text-zinc-200"
                >
                  <option value="low">Low Sensitivity</option>
                  <option value="medium">Medium (Default)</option>
                  <option value="high">High Sensitivity (Strict)</option>
                  <option value="off">Off (Permissive)</option>
                </select>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="hitl-new"
                  checked={newHitl}
                  onChange={(e) => setNewHitl(e.target.checked)}
                  className="w-4 h-4 accent-indigo-600"
                />
                <label htmlFor="hitl-new" className="text-xs text-zinc-300">
                  Enable Human-in-the-Loop review holds
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-3 py-1.5 rounded-lg border border-white/10 text-zinc-400 hover:text-white text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-md shadow-indigo-600/30"
                >
                  {creating ? "Provisioning..." : "Create Inbox"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
