"use client";

import { usePathname } from "next/navigation";
import { ShieldCheck, Sparkles, Terminal, Bell } from "lucide-react";
import Link from "next/link";

export function Header() {
  const pathname = usePathname();

  const getPageTitle = () => {
    switch (pathname) {
      case "/":
        return { title: "Mission Control", subtitle: "Real-time telemetry, threat mitigation & inbox activity" };
      case "/inbox":
        return { title: "Two-Way Agent Inboxes", subtitle: "RFC-threaded messaging with SPF, DKIM & DMARC proof" };
      case "/reviews":
        return { title: "Human-in-the-Loop Review Queue", subtitle: "Inspect and resolve suspicious prompt-injection payloads" };
      case "/simulator":
        return { title: "Threat Lab & Simulator", subtitle: "Inject realistic attacks and evaluate real-time protection filters" };
      case "/agents":
        return { title: "Agent Directory & Posture", subtitle: "Configure inboxes, threat scan sensitivity & auto-reply prompts" };
      case "/mcp":
        return { title: "Model Context Protocol (MCP)", subtitle: "Connect Cursor, Claude Code, and autonomous coding agents" };
      default:
        return { title: "Dashboard", subtitle: "Open Agent Email Gateway" };
    }
  };

  const info = getPageTitle();

  return (
    <header className="h-16 border-b border-white/5 bg-[#090c10]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
          {info.title}
          <span className="text-[10px] font-normal text-zinc-300 font-mono hidden md:inline">
            // {info.subtitle}
          </span>
        </h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Domain Badge */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.03] border border-white/10 text-xs text-zinc-300">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-mono text-[11px] text-zinc-300">@agents.local</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        </div>

        {/* Quick Simulator CTA */}
        <Link
          href="/simulator"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm shadow-indigo-600/30 transition-all hover:scale-[1.02]"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Test Inbound</span>
        </Link>

        {/* API Docs link */}
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="p-2 rounded-lg border border-white/10 text-zinc-400 hover:text-white hover:bg-white/5 transition-all text-xs"
          title="OpenAPI Documentation"
        >
          <Terminal className="w-4 h-4" />
        </a>
      </div>
    </header>
  );
}
