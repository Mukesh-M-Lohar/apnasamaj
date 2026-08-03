"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/api/client";
import { useAuthStore } from "@/store/auth";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);

  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const requestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.post("/auth/otp/request", { mobile: phone });
      setStep("otp");
      // The backend returns OTP in dev mode, we can pre-fill it for convenience in testing
      if (res.data?.otp) {
        setOtp(res.data.otp);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to send OTP");
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.post("/auth/otp/verify", { mobile: phone, otp });
      const { access_token, user, tenant } = res.data;

      const tenantId = tenant?.id || "";

      setAuth(access_token, tenantId, {
        id: user.id,
        phone_number: user.mobile,
        role: tenantId ? "admin" : "super_admin",
      });

      router.push("/");
    } catch (err: any) {
      setError(err.response?.data?.message || "Invalid OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", backgroundColor: "var(--background-alt)" }}>
      <div className="card" style={{ maxWidth: "400px", width: "100%", padding: "2rem" }}>
        <h1 style={{ textAlign: "center", marginBottom: "0.5rem" }}>ApnaSamaj</h1>
        <p style={{ textAlign: "center", color: "var(--text-secondary)", marginBottom: "2rem" }}>
          Community Operations Center
        </p>

        {error && (
          <div style={{ backgroundColor: "var(--danger)", color: "white", padding: "0.75rem", borderRadius: "8px", marginBottom: "1rem", fontSize: "0.875rem" }}>
            {error}
          </div>
        )}

        {step === "phone" ? (
          <form onSubmit={requestOtp}>
            <div className="input-group">
              <label className="label">Mobile Number</label>
              <input
                type="tel"
                className="input"
                placeholder="+919876543210"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: "100%", marginTop: "1rem" }} disabled={loading}>
              {loading ? "Sending..." : "Send OTP"}
            </button>
          </form>
        ) : (
          <form onSubmit={verifyOtp}>
            <div className="input-group">
              <label className="label">Enter OTP</label>
              <input
                type="text"
                className="input"
                placeholder="123456"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
              />
              <p style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginTop: "0.5rem" }}>
                Sent to {phone}. <span style={{ color: "var(--primary)", cursor: "pointer" }} onClick={() => setStep("phone")}>Change number</span>
              </p>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: "100%", marginTop: "1rem" }} disabled={loading}>
              {loading ? "Verifying..." : "Verify & Login"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
