"use client";

import { useEffect, useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  UserCheck,
  MessageSquare,
  Lock,
  ArrowRight,
  RefreshCw
} from "lucide-react";
import { api } from "@/lib/api";
import { ReviewItem } from "@/lib/types";

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [selectedReview, setSelectedReview] = useState<ReviewItem | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("pending");
  const [reviewerNotes, setReviewerNotes] = useState<string>("");
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const loadReviews = async () => {
    try {
      setLoading(true);
      const items = await api.getReviews(statusFilter || undefined);
      setReviews(items);
      if (items.length > 0) {
        setSelectedReview(items[0]);
      } else {
        setSelectedReview(null);
      }
    } catch (err) {
      console.error("Failed to fetch reviews:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviews();
  }, [statusFilter]);

  const handleApprove = async () => {
    if (!selectedReview) return;
    try {
      setActionLoading(true);
      const updated = await api.approveReview(
        selectedReview.id,
        reviewerNotes || "Approved and cleared by human supervisor"
      );
      setReviewerNotes("");
      await loadReviews();
      setSelectedReview(updated);
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedReview) return;
    try {
      setActionLoading(true);
      const updated = await api.rejectReview(
        selectedReview.id,
        reviewerNotes || "Quarantined due to malicious prompt injection vector"
      );
      setReviewerNotes("");
      await loadReviews();
      setSelectedReview(updated);
    } catch (err: any) {
      alert(`Rejection error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 border-amber-500/20 bg-amber-500/[0.02]">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Human-in-the-Loop (HITL) Gate
            </h2>
            <p className="text-xs text-zinc-300 mt-0.5">
              Emails held in <code className="text-amber-300 font-mono">pending_review</code> status before AI agents can execute them.
            </p>
          </div>
        </div>

        {/* Status Tab Filters */}
        <div className="flex items-center gap-2 bg-[#090c10] p-1 rounded-xl border border-white/10 text-xs">
          <button
            onClick={() => setStatusFilter("pending")}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              statusFilter === "pending"
                ? "bg-amber-500 text-black font-semibold shadow-md shadow-amber-500/20"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            Pending ({reviews.filter((r) => r.status === "pending").length})
          </button>
          <button
            onClick={() => setStatusFilter("approved")}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              statusFilter === "approved"
                ? "bg-emerald-600 text-white font-semibold"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            Approved
          </button>
          <button
            onClick={() => setStatusFilter("rejected")}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              statusFilter === "rejected"
                ? "bg-rose-600 text-white font-semibold"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            Quarantined
          </button>
        </div>
      </div>

      {/* Main Review Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[580px]">
        {/* Left: Queue List */}
        <div className="lg:col-span-5 glass-panel rounded-2xl flex flex-col overflow-hidden">
          <div className="p-3.5 border-b border-white/5 flex items-center justify-between text-xs text-zinc-400">
            <span className="font-semibold text-white">Review Items</span>
            <button onClick={loadReviews} className="flex items-center gap-1 hover:text-white">
              <RefreshCw className="w-3 h-3" /> Refresh
            </button>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-white/5">
            {reviews.length === 0 ? (
              <div className="p-12 text-center text-zinc-400 text-xs">
                No items currently in this review status.
              </div>
            ) : (
              reviews.map((rev) => {
                const isSelected = selectedReview?.id === rev.id;
                return (
                  <div
                    key={rev.id}
                    onClick={() => setSelectedReview(rev)}
                    className={`p-4 cursor-pointer transition-all ${
                      isSelected
                        ? "bg-amber-500/10 border-l-4 border-amber-500"
                        : "hover:bg-white/[0.02]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-xs font-semibold text-zinc-200 truncate">
                        {rev.agent_email}
                      </span>
                      <span className="text-[10px] font-mono text-zinc-300">
                        {new Date(rev.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>

                    <div className="text-xs font-medium text-white truncate mb-1">
                      {rev.message?.subject || "Subject review"}
                    </div>

                    <p className="text-[11px] text-zinc-400 line-clamp-2">
                      {rev.reason}
                    </p>

                    <div className="flex items-center gap-2 mt-2">
                      <span
                        className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                          rev.status === "pending"
                            ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                            : rev.status === "approved"
                            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                            : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                        }`}
                      >
                        {rev.status}
                      </span>

                      <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300">
                        Score {Math.round(rev.threat_score * 100)}%
                      </span>

                      <span className="text-[10px] text-zinc-300 font-mono ml-auto">
                        ID: {rev.id}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Security Deep-Dive & Action Console */}
        <div className="lg:col-span-7 glass-panel rounded-2xl flex flex-col overflow-hidden">
          {selectedReview ? (
            <div className="flex-1 flex flex-col h-full">
              {/* Header Info */}
              <div className="p-6 border-b border-white/5 space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-zinc-400 border border-white/10 uppercase">
                        Review {selectedReview.id}
                      </span>
                      <span className="text-xs text-zinc-300 font-mono">
                        Message ID: {selectedReview.message_id}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mt-1">
                      {selectedReview.message?.subject || "(No Subject)"}
                    </h3>
                  </div>

                  <span
                    className={`text-xs font-mono font-bold px-3 py-1 rounded-full uppercase ${
                      selectedReview.threat_score >= 0.8
                        ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                        : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                    }`}
                  >
                    Risk {Math.round(selectedReview.threat_score * 100)}%
                  </span>
                </div>

                {/* Threat Diagnostic Box */}
                <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-rose-300">
                    <ShieldAlert className="w-4 h-4 text-rose-400" />
                    <span>Scan Verdict: {selectedReview.reason}</span>
                  </div>
                  <div className="text-[11px] text-rose-200/80 font-mono">
                    Sender: {selectedReview.message?.sender} → Target: {selectedReview.agent_email}
                  </div>
                </div>
              </div>

              {/* Message Payload Body Inspection */}
              <div className="p-6 flex-1 overflow-y-auto space-y-3">
                <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 block">
                  Original Raw Email Content
                </label>
                <div className="p-4 rounded-xl bg-[#090c10] border border-white/10 font-mono text-xs text-zinc-200 whitespace-pre-wrap leading-relaxed select-text">
                  {selectedReview.message?.body_text}
                </div>

                {selectedReview.message?.body_html && (
                  <div className="space-y-1 pt-2">
                    <label className="text-[10px] font-bold uppercase text-zinc-500 block">
                      HTML Source (Concealed Attributes)
                    </label>
                    <div className="p-3 rounded-lg bg-[#090c10] border border-white/10 font-mono text-[11px] text-amber-300/80 overflow-x-auto">
                      {selectedReview.message.body_html}
                    </div>
                  </div>
                )}
              </div>

              {/* Resolution Controls */}
              <div className="p-5 border-t border-white/5 bg-[#0a0d14]/80 space-y-3">
                {selectedReview.status === "pending" ? (
                  <>
                    <input
                      type="text"
                      placeholder="Add supervisor notes (optional)..."
                      value={reviewerNotes}
                      onChange={(e) => setReviewerNotes(e.target.value)}
                      className="w-full bg-[#090c10] border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500 font-sans"
                    />
                    <div className="flex items-center justify-end gap-3">
                      <button
                        onClick={handleReject}
                        disabled={actionLoading}
                        className="px-4 py-2 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-xs font-semibold flex items-center gap-1.5 transition-all"
                      >
                        <XCircle className="w-4 h-4 text-rose-400" />
                        <span>Reject & Quarantine</span>
                      </button>

                      <button
                        onClick={handleApprove}
                        disabled={actionLoading}
                        className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-emerald-600/30 transition-all"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Approve & Deliver to Agent</span>
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center justify-between text-xs text-zinc-400">
                    <span className="flex items-center gap-2">
                      <UserCheck className="w-4 h-4 text-indigo-400" />
                      Status: <strong className="text-white capitalize">{selectedReview.status}</strong>
                    </span>
                    <span className="font-mono text-[11px] text-zinc-300">
                      Resolved: {selectedReview.resolved_at ? new Date(selectedReview.resolved_at).toLocaleString() : "Yes"}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center text-zinc-400">
              <ShieldAlert className="w-12 h-12 text-zinc-600 mb-3" />
              <p className="text-sm font-medium text-zinc-300">Select an item from the review queue</p>
              <p className="text-xs text-zinc-500 mt-1">
                Held messages remain paused until human action or expiration.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
