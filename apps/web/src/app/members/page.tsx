"use client";

import { useEffect, useState } from "react";
import { Search, Plus } from "lucide-react";
import { apiClient } from "@/api/client";

interface Member {
  id: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  is_active: boolean;
  role: string;
  created_at: string;
}

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    // In a real app we fetch from apiClient.get('/members')
    // We mock the response here to demonstrate the UI
    setTimeout(() => {
      setMembers([
        { id: "1", first_name: "Rahul", last_name: "Sharma", phone_number: "+919876543210", is_active: true, role: "admin", created_at: "2026-01-15T00:00:00Z" },
        { id: "2", first_name: "Priya", last_name: "Patel", phone_number: "+919876543211", is_active: true, role: "member", created_at: "2026-02-10T00:00:00Z" },
        { id: "3", first_name: "Amit", last_name: "Verma", phone_number: "+919876543212", is_active: false, role: "member", created_at: "2026-03-05T00:00:00Z" },
      ]);
      setLoading(false);
    }, 800);
  }, []);

  const filteredMembers = members.filter((m) => 
    `${m.first_name} ${m.last_name}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Member Directory</h1>
        <button className="btn btn-primary">
          <Plus size={18} />
          Add Member
        </button>
      </div>

      <div className="card">
        {/* Toolbar */}
        <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
          <div className="input-group" style={{ flex: 1, margin: 0 }}>
            <div style={{ position: "relative" }}>
              <Search size={18} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
              <input 
                type="text" 
                className="input" 
                placeholder="Search by name or phone..." 
                style={{ paddingLeft: "2.5rem" }}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
          <button className="btn btn-outline">Export CSV</button>
        </div>

        {/* Datagrid */}
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Phone Number</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "2rem" }}>Loading...</td>
                </tr>
              ) : filteredMembers.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "2rem" }}>No members found.</td>
                </tr>
              ) : (
                filteredMembers.map((member) => (
                  <tr key={member.id}>
                    <td style={{ fontWeight: 500 }}>{member.first_name} {member.last_name}</td>
                    <td>{member.phone_number}</td>
                    <td style={{ textTransform: "capitalize" }}>{member.role}</td>
                    <td>
                      <span className={`badge ${member.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {member.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>{new Date(member.created_at).toLocaleDateString()}</td>
                    <td>
                      <button style={{ color: "var(--primary)", fontWeight: 500 }}>Edit</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
