"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowRight
} from "lucide-react";
import { api } from "@/lib/api";
import { Agent, ThreatScanResult, Message } from "@/lib/types";
import { Dropdown } from "@/components/Dropdown";

interface SimulationResult {
  message: Message;
  threat_scan: ThreatScanResult;
  action_taken: string;
  review_id?: string;
}

export default function SimulatorPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>("");

  // Form Fields
  const [sender, setSender] = useState<string>("customer@example.com");
  const [subject, setSubject] = useState<string>("Support inquiry");
  const [bodyText, setBodyText] = useState<string>(
    "Hello team, could you please provide assistance with our account setup?"
  );
  const [bodyHtml, setBodyHtml] = useState<string>("");
  const [spfStatus, setSpfStatus] = useState<string>("pass");
  const [dkimStatus, setDkimStatus] = useState<string>("pass");
  const [dmarcStatus, setDmarcStatus] = useState<string>("pass");

  const [simulating, setSimulating] = useState<boolean>(false);
  const [result, setResult] = useState<SimulationResult | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const ags = await api.getAgents();
        setAgents(ags);
        if (ags.length > 0) setSelectedAgent(ags[0].email);
      } catch (err) {
        console.error(err);
      }
    };
    fetchAgents();
  }, []);

  const runSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent) return;
    try {
      setSimulating(true);
      const res = await api.simulateInbound({
        agent_email: selectedAgent,
        sender,
        subject,
        body_text: bodyText,
        body_html: bodyHtml || undefined,
        spf_status: spfStatus,
        dkim_status: dkimStatus,
        dmarc_status: dmarcStatus,
        verified_domain: spfStatus === "pass" ? sender.split("@")[-1] : undefined,
      });
      setResult(res);
    } catch (err: any) {
      alert(`Simulation error: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  const agentOptions = agents.map((ag) => ({
    value: ag.email,
    label: `${ag.display_name} (${ag.email})`,
  }));

  const spfOptions = [
    { value: "pass", label: "SPF: Pass" },
    { value: "fail", label: "SPF: Fail" },
    { value: "neutral", label: "SPF: Neutral" },
  ];

  const dkimOptions = [
    { value: "pass", label: "DKIM: Pass" },
    { value: "fail", label: "DKIM: Fail" },
    { value: "none", label: "DKIM: None" },
  ];

  return (
    <div className="space-y-4">
      <div className="card-simple p-4">
        <h2 className="text-sm font-semibold text-[#e6edf3]">
          Inbound Email Threat Simulator
        </h2>
        <p className="text-xs text-[#8b949e]">
          Send a simulated email payload to an agent inbox and test the heuristic prompt injection filter.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left: Input Form */}
        <div className="lg:col-span-6 card-simple p-4 space-y-3">
          <div className="text-xs font-semibold text-[#e6edf3]">
            Input Email Details
          </div>

          <form onSubmit={runSimulation} className="space-y-3 text-xs">
            <div>
              <Dropdown
                label="Target Agent Inbox"
                options={agentOptions}
                value={selectedAgent}
                onChange={setSelectedAgent}
                placeholder={agents.length === 0 ? "No agents created yet" : "Select Agent"}
              />
            </div>

            <div>
              <label className="text-[#8b949e] block mb-1">Sender Email</label>
              <input
                type="text"
                required
                value={sender}
                onChange={(e) => setSender(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] font-mono focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <Dropdown
                  label="SPF Status"
                  options={spfOptions}
                  value={spfStatus}
                  onChange={setSpfStatus}
                />
              </div>
              <div>
                <Dropdown
                  label="DKIM Status"
                  options={dkimOptions}
                  value={dkimStatus}
                  onChange={setDkimStatus}
                />
              </div>
            </div>

            <div>
              <label className="text-[#8b949e] block mb-1">Subject</label>
              <input
                type="text"
                required
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div>
              <label className="text-[#8b949e] block mb-1">Email Body (Text)</label>
              <textarea
                rows={5}
                required
                value={bodyText}
                onChange={(e) => setBodyText(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] font-mono focus:outline-none focus:border-zinc-500 resize-none"
              />
            </div>

            <div>
              <label className="text-[#8b949e] block mb-1">Optional HTML Body (Hidden text, tags)</label>
              <textarea
                rows={2}
                value={bodyHtml}
                onChange={(e) => setBodyHtml(e.target.value)}
                placeholder="Optional HTML content..."
                className="w-full bg-[#0d1117] border border-[#30363d] rounded p-2 text-xs text-[#e6edf3] font-mono focus:outline-none focus:border-zinc-500 resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={simulating || !selectedAgent}
              className="w-full py-2 rounded bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{simulating ? "Processing..." : "Submit Email"}</span>
            </button>
          </form>
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-6 card-simple p-4 flex flex-col justify-between">
          <div>
            <div className="text-xs font-semibold text-[#e6edf3] mb-3">
              Diagnostic & Action Taken
            </div>

            {result ? (
              <div className="space-y-4">
                {/* Result Status Card */}
                <div
                  className={`p-3.5 rounded border text-xs space-y-1 ${
                    result.threat_scan.verdict === "block"
                      ? "bg-[#da3633]/10 border-[#f85149]/30 text-[#f85149]"
                      : result.threat_scan.verdict === "review"
                      ? "bg-[#9e6a03]/10 border-[#d29922]/30 text-[#d29922]"
                      : "bg-[#238636]/10 border-[#2ea043]/30 text-[#2ea043]"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                      {result.threat_scan.verdict === "block" && <XCircle className="w-4 h-4" />}
                      {result.threat_scan.verdict === "review" && <Clock className="w-4 h-4" />}
                      {result.threat_scan.verdict === "allow" && <CheckCircle2 className="w-4 h-4" />}
                      Action: {result.action_taken.replace("_", " ")}
                    </span>
                    <span className="font-mono text-xs font-bold">
                      Risk Score: {Math.round(result.threat_scan.threat_score * 100)}%
                    </span>
                  </div>
                  <div className="text-[11px] opacity-90">
                    {result.threat_scan.analysis_summary}
                  </div>
                </div>

                {/* Detected Threat Details */}
                <div className="space-y-2">
                  <div className="text-xs font-medium text-[#8b949e]">
                    Detected Signals ({result.threat_scan.detected_threats.length})
                  </div>

                  {result.threat_scan.detected_threats.length === 0 ? (
                    <div className="p-3 rounded bg-[#0d1117] border border-[#30363d] text-xs text-[#2ea043]">
                      No malicious prompt injection signals detected.
                    </div>
                  ) : (
                    <div className="space-y-1.5">
                      {result.threat_scan.detected_threats.map((t, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded bg-[#0d1117] border border-[#30363d] space-y-1 text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-[#e6edf3]">{t.description}</span>
                            <span className="text-[10px] font-mono text-[#f85149] uppercase">
                              {t.threat_type} · {t.severity}
                            </span>
                          </div>
                          {t.matched_pattern && (
                            <div className="font-mono text-[10px] text-[#8b949e] truncate">
                              Matched: {t.matched_pattern}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Stored IDs */}
                <div className="p-2.5 rounded bg-[#0d1117] border border-[#30363d] text-xs text-[#8b949e] space-y-1">
                  <div className="flex justify-between">
                    <span>Message ID:</span>
                    <span className="font-mono text-[#e6edf3]">{result.message.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Thread ID:</span>
                    <span className="font-mono text-[#e6edf3]">{result.message.thread_id}</span>
                  </div>
                  {result.review_id && (
                    <div className="pt-1.5 flex justify-between border-t border-[#30363d]">
                      <span className="text-[#d29922]">Held in Review:</span>
                      <Link href="/reviews" className="text-blue-400 hover:underline flex items-center gap-1">
                        Go to Review Queue <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-xs text-[#8b949e]">
                Fill out the form on the left and click &quot;Submit Email&quot; to test.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
