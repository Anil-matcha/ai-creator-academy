"use client";

import { usePathname } from "next/navigation";
import { Terminal, Shield } from "lucide-react";
import Link from "next/link";

export function Header() {
  const pathname = usePathname();

  const getPageTitle = () => {
    switch (pathname) {
      case "/":
        return { title: "Overview", subtitle: "System telemetry and email activity" };
      case "/inbox":
        return { title: "Inboxes", subtitle: "Two-way email threads" };
      case "/reviews":
        return { title: "Review Queue", subtitle: "Held messages awaiting human review" };
      case "/simulator":
        return { title: "Simulator", subtitle: "Test inbound email threat scanner" };
      case "/agents":
        return { title: "Agent Directory", subtitle: "Manage email inboxes and policies" };
      case "/mcp":
        return { title: "MCP Integration", subtitle: "Connect Cursor and Claude Code" };
      default:
        return { title: "Dashboard", subtitle: "Open Agent Email Gateway" };
    }
  };

  const info = getPageTitle();

  return (
    <header className="h-14 border-b border-[#30363d] bg-[#161b22] px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-sm font-semibold text-[#e6edf3] flex items-center gap-2">
          {info.title}
          <span className="text-xs font-normal text-[#8b949e] hidden md:inline">
            — {info.subtitle}
          </span>
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded border border-[#30363d] bg-[#0d1117] text-xs text-[#8b949e]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#2ea043]" />
          <span className="font-mono text-[11px] text-[#e6edf3]">@agents.local</span>
        </div>

        <Link
          href="/simulator"
          className="px-3 py-1 rounded border border-[#30363d] bg-[#21262d] hover:bg-[#30363d] text-xs font-medium text-[#e6edf3] transition-colors"
        >
          Test Inbound
        </Link>

        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="p-1.5 rounded border border-[#30363d] text-[#8b949e] hover:text-[#e6edf3] hover:bg-[#21262d] transition-colors text-xs"
          title="OpenAPI Documentation"
        >
          <Terminal className="w-3.5 h-3.5" />
        </a>
      </div>
    </header>
  );
}
