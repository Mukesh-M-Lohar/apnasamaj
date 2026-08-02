"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Building,
  CreditCard,
  MessageSquareWarning,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/store/auth";

export default function Sidebar() {
  const pathname = usePathname();
  const logout = useAuthStore((state) => state.logout);

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Members", href: "/members", icon: Users },
    { name: "Donations", href: "/donations", icon: CreditCard },
    { name: "Facilities", href: "/facilities", icon: Building },
    { name: "Complaints", href: "/complaints", icon: MessageSquareWarning },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Building size={28} />
          ApnaSamaj Admin
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${isActive ? "active" : ""}`}
            >
              <Icon size={20} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-nav" style={{ flex: "none", borderTop: "1px solid var(--border-color)" }}>
        <button className="nav-item" onClick={logout} style={{ width: "100%" }}>
          <LogOut size={20} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
