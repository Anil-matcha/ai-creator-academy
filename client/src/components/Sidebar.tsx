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
    },
    { name: "Simulator", href: "/simulator", icon: FlaskConical },
    { name: "Agents", href: "/agents", icon: Bot },
    { name: "MCP Server", href: "/mcp", icon: Cpu },
  ];

  return (
    <aside className="w-56 border-r border-[#30363d] bg-[#161b22] flex flex-col justify-between h-screen sticky top-0 shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="p-4 border-b border-[#30363d]">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-[#238636] flex items-center justify-center text-white font-bold text-xs">
              <Mail className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-[#e6edf3] tracking-tight">
                Open Agent Email
              </div>
              <div className="text-[10px] text-[#8b949e]">Gateway & Inboxes</div>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="p-2 space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-[#21262d] text-white font-semibold"
                    : "text-[#8b949e] hover:text-[#e6edf3] hover:bg-[#21262d]/50"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4 text-[#8b949e]" />
                  <span>{item.name}</span>
                </div>
                {item.badge !== undefined && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 bg-[#9e6a03]/30 text-[#d29922] border border-[#d29922]/30 rounded">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>      
    </aside>
  );
}
