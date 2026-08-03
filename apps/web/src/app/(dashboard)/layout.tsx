"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { useAuthStore } from "@/store/auth";

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const token = useAuthStore((state) => state.token);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!token) {
      router.push("/login");
    }
  }, [token, router]);

  if (!mounted) return null;

  // If we are redirecting, render nothing to avoid flash of content
  if (!token) return null;

  return (
    <div className="admin-layout">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <h2 style={{ fontSize: "1.125rem", color: "var(--text-secondary)" }}>
            Community Operations Center
          </h2>
          <div className="badge badge-primary">Admin Session Active</div>
        </header>

        <div className="page-container animate-fade-in">
          {children}
        </div>
      </main>
    </div>
  );
}
