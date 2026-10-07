"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  Mail,
  ShieldAlert,
  FlaskConical,
  Bot,
  Cpu,
  Radio,
  ExternalLink
} from "lucide-react";
import { api } from "@/lib/api";

export function Sidebar() {
  const pathname = usePathname();
  const [pendingReviews, setPendingReviews] = useState<number>(0);

  useEffect(() => {
    const fetchPending = async () => {
      try {
        const stats = await api.getStats();
        setPendingReviews(stats.pending_reviews);
      } catch {
        // quiet fallback
      }
    };
    fetchPending();
    const interval = setInterval(fetchPending, 5000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: "Overview", href: "/", icon: LayoutDashboard },
    { name: "Two-Way Inbox", href: "/inbox", icon: Mail },
    {
      name: "HITL Reviews",
      href: "/reviews",
      icon: ShieldAlert,
      badge: pendingReviews > 0 ? pendingReviews : undefined,
      badgeColor: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
    },
    { name: "Threat Simulator", href: "/simulator", icon: FlaskConical },
    { name: "Agent Inboxes", href: "/agents", icon: Bot },
    { name: "MCP Server", href: "/mcp", icon: Cpu },
  ];

  return (
    <aside className="w-64 border-r border-white/5 bg-[#0a0d14]/90 flex flex-col justify-between h-screen sticky top-0 backdrop-blur-xl z-30">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-white/5 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-[1px] shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all">
              <div className="w-full h-full bg-[#0a0d14] rounded-[11px] flex items-center justify-center">
                <Mail className="w-4 h-4 text-indigo-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-sm tracking-tight text-white group-hover:text-indigo-300 transition-colors">
                  Open Agent
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  EMAIL
                </span>
              </div>
              <p className="text-[11px] text-zinc-400">Agent Inboxes & Security</p>
            </div>
          </Link>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-2 text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
            Platform
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/25 shadow-sm shadow-indigo-500/10 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? "text-indigo-400" : "text-zinc-400 group-hover:text-zinc-300"
                    }`}
                  />
                  <span>{item.name}</span>
                </div>
                {item.badge !== undefined && (
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${item.badgeColor}`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-white/5 space-y-3">
        <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-zinc-300 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 live-pulse inline-block" />
              FastAPI Core
            </span>
            <span className="text-[10px] font-mono text-emerald-400">ONLINE</span>
          </div>
          <div className="text-[10px] text-zinc-400 flex items-center justify-between">
            <span>Port 8000</span>
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-indigo-400 hover:underline flex items-center gap-1"
            >
              OpenAPI <ExternalLink className="w-2.5 h-2.5" />
            </a>
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] text-zinc-400 px-1">
          <span className="flex items-center gap-1">
            <Radio className="w-3 h-3 text-indigo-400" />
            WebSocket Push
          </span>
          <span className="text-[10px] text-zinc-400 font-mono">Ready</span>
        </div>
      </div>
    </aside>
  );
}
