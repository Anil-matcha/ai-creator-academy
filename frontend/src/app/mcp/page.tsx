"use client";

import { useEffect, useState } from "react";
import {
  Cpu,
  Copy,
  Check,
  Terminal,
  ExternalLink,
  Bot,
  Zap,
  Code2,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { api } from "@/lib/api";

export default function McpPage() {
  const [copiedCursor, setCopiedCursor] = useState<boolean>(false);
  const [copiedClaude, setCopiedClaude] = useState<boolean>(false);
  const [mcpInfo, setMcpInfo] = useState<any>(null);

  useEffect(() => {
    const fetchMcp = async () => {
      try {
        const info = await api.getMcpInfo();
        setMcpInfo(info);
      } catch (err) {
        console.error(err);
      }
    };
    fetchMcp();
  }, []);

  const cursorJson = JSON.stringify(
    {
      mcpServers: {
        "open-agent-email": {
          url: "http://127.0.0.1:8000/mcp/rpc",
        },
      },
    },
    null,
    2
  );

  const claudeCommand = "claude mcp add open-agent-email http://127.0.0.1:8000/mcp/rpc";

  const copyToClipboard = (text: string, type: "cursor" | "claude") => {
    navigator.clipboard.writeText(text);
    if (type === "cursor") {
      setCopiedCursor(true);
      setTimeout(() => setCopiedCursor(false), 2000);
    } else {
      setCopiedClaude(true);
      setTimeout(() => setCopiedClaude(false), 2000);
    }
  };

  const tools = [
    {
      name: "list_agents",
      description: "Lists all configured AI agent email addresses and statuses.",
      sampleParams: "{}",
    },
    {
      name: "list_messages",
      description: "Fetches recent emails received or sent by an agent inbox.",
      sampleParams: '{"agent_email": "support@agents.local", "status": "delivered"}',
    },
    {
      name: "get_message",
      description: "Reads full email body, RFC headers, and SPF/DKIM verification tags.",
      sampleParams: '{"agent_email": "support@agents.local", "message_id": "msg_..."}',
    },
    {
      name: "send_message",
      description: "Dispatches a new outbound email from the agent's verified address.",
      sampleParams: '{"agent_email": "support@agents.local", "recipient": "user@example.com", "subject": "Hello", "body_text": "..."}',
    },
    {
      name: "reply_to_message",
      description: "Replies in-thread to an existing email, preserving RFC Message-ID and In-Reply-To.",
      sampleParams: '{"agent_email": "support@agents.local", "message_id": "msg_...", "body_text": "Got it!"}',
    },
    {
      name: "list_reviews",
      description: "Fetches emails held in the Human-in-the-Loop review queue.",
      sampleParams: '{"status": "pending"}',
    },
    {
      name: "approve_review",
      description: "Approves a held email and delivers it to the target agent.",
      sampleParams: '{"review_id": "rev_...", "notes": "Approved via MCP"}',
    },
    {
      name: "reject_review",
      description: "Quarantines a dangerous prompt injection email from delivery.",
      sampleParams: '{"review_id": "rev_...", "notes": "Prompt injection detected"}',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="glass-panel p-8 rounded-2xl border-indigo-500/20 bg-gradient-to-br from-indigo-950/30 via-[#0d121c] to-[#090c10] space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[10px] font-mono">
              Model Context Protocol (MCP) · JSON-RPC 2.0
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight mt-1">
              Connect Coding Agents Directly to Agent Inboxes
            </h2>
          </div>
        </div>
        <p className="text-xs text-zinc-300 max-w-3xl leading-relaxed">
          Point Cursor, Claude Code, Windsurf, or custom LangChain/CrewAI agents at the MCP server endpoint. Your agents can read inbound mail, reply in-thread, and interact with the Human-in-the-Loop review queue natively as tool calls.
        </p>
      </div>

      {/* Integration Snippets: Cursor & Claude Code */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cursor Config */}
        <div className="glass-panel p-6 rounded-2xl space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-white flex items-center gap-2">
                <Code2 className="w-4 h-4 text-indigo-400" />
                Cursor Configuration
              </span>
              <span className="text-[11px] font-mono text-zinc-400">.cursor/mcp.json</span>
            </div>
            <p className="text-xs text-zinc-400">
              Paste this snippet into your workspace <code className="text-zinc-200">.cursor/mcp.json</code> or global config.
            </p>
            <div className="relative">
              <pre className="p-4 rounded-xl bg-[#090c10] border border-white/10 font-mono text-xs text-zinc-200 overflow-x-auto">
                {cursorJson}
              </pre>
            </div>
          </div>

          <button
            onClick={() => copyToClipboard(cursorJson, "cursor")}
            className="w-full mt-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-white flex items-center justify-center gap-2 transition-all"
          >
            {copiedCursor ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copiedCursor ? "Copied Cursor Config!" : "Copy Cursor JSON"}</span>
          </button>
        </div>

        {/* Claude Code CLI */}
        <div className="glass-panel p-6 rounded-2xl space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-white flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                Claude Code CLI
              </span>
              <span className="text-[11px] font-mono text-zinc-400">Terminal Command</span>
            </div>
            <p className="text-xs text-zinc-400">
              Run this single command in your terminal to register the tool suite with Claude Code:
            </p>
            <div className="relative">
              <pre className="p-4 rounded-xl bg-[#090c10] border border-white/10 font-mono text-xs text-cyan-300 overflow-x-auto whitespace-pre-wrap">
                {claudeCommand}
              </pre>
            </div>
          </div>

          <button
            onClick={() => copyToClipboard(claudeCommand, "claude")}
            className="w-full mt-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-white flex items-center justify-center gap-2 transition-all"
          >
            {copiedClaude ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copiedClaude ? "Copied Claude Command!" : "Copy CLI Command"}</span>
          </button>
        </div>
      </div>

      {/* Available MCP Tools Catalog */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-400" />
              Registered MCP Toolset ({tools.length} Tools)
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Callable by any MCP client over Streamable HTTP RPC.
            </p>
          </div>
          <span className="text-[10px] font-mono px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            RPC Active on :8000
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {tools.map((tool) => (
            <div key={tool.name} className="p-4 rounded-xl bg-[#090c10] border border-white/5 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-indigo-400">{tool.name}</span>
                <span className="text-[10px] text-zinc-400 font-mono">Tool</span>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed">{tool.description}</p>
              <div className="pt-2 border-t border-white/5">
                <span className="text-[10px] font-mono text-zinc-400 block mb-0.5">Example Arguments:</span>
                <code className="text-[11px] font-mono text-zinc-300 bg-black/40 px-2 py-1 rounded block truncate">
                  {tool.sampleParams}
                </code>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
