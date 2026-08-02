"use client";

import { useEffect, useState } from "react";
import { Users, Banknote, CalendarCheck, AlertOctagon } from "lucide-react";
import { apiClient } from "@/api/client";

interface DashboardMetrics {
  totalMembers: number;
  fundsRaised: number;
  upcomingEvents: number;
  openComplaints: number;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalMembers: 0,
    fundsRaised: 0,
    upcomingEvents: 0,
    openComplaints: 0,
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real scenario, this fetches from an aggregated dashboard API
    // We simulate fetching here to demonstrate the UI
    setTimeout(() => {
      setMetrics({
        totalMembers: 245,
        fundsRaised: 142500,
        upcomingEvents: 4,
        openComplaints: 3,
      });
      setLoading(false);
    }, 800);
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: "2rem" }}>Dashboard Overview</h1>

      <div className="metric-grid">
        {/* Metric 1 */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>Total Members</h3>
            <Users color="var(--primary)" />
          </div>
          <div className="metric-value">
            {loading ? "..." : metrics.totalMembers}
          </div>
          <p style={{ fontSize: "0.875rem", marginTop: "0.5rem" }}>
            <span style={{ color: "var(--success)" }}>+12</span> from last month
          </p>
        </div>

        {/* Metric 2 */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>Funds Raised (₹)</h3>
            <Banknote color="var(--success)" />
          </div>
          <div className="metric-value">
            {loading ? "..." : `₹${metrics.fundsRaised.toLocaleString()}`}
          </div>
          <p style={{ fontSize: "0.875rem", marginTop: "0.5rem" }}>
            <span style={{ color: "var(--success)" }}>+8.4%</span> vs last year
          </p>
        </div>

        {/* Metric 3 */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>Upcoming Events</h3>
            <CalendarCheck color="#f59e0b" />
          </div>
          <div className="metric-value">
            {loading ? "..." : metrics.upcomingEvents}
          </div>
          <p style={{ fontSize: "0.875rem", marginTop: "0.5rem" }}>
            Next event in 4 days
          </p>
        </div>

        {/* Metric 4 */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>Open Complaints</h3>
            <AlertOctagon color="var(--danger)" />
          </div>
          <div className="metric-value">
            {loading ? "..." : metrics.openComplaints}
          </div>
          <p style={{ fontSize: "0.875rem", marginTop: "0.5rem" }}>
            <span style={{ color: "var(--danger)" }}>1</span> Critical issue
          </p>
        </div>
      </div>
      
      <div className="card" style={{ marginTop: "2rem" }}>
        <h2>Recent Activity</h2>
        <p>Your community's pulse for the last 48 hours.</p>
        {/* Placeholder for an activity feed component */}
        <div style={{ marginTop: "1.5rem", padding: "2rem", textAlign: "center", border: "1px dashed var(--border-color)", borderRadius: "var(--radius-md)" }}>
          <p>No recent activity.</p>
        </div>
      </div>
    </div>
  );
}
