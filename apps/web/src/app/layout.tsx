import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ApnaSamaj | Admin Portal",
  description: "Web Admin Dashboard for Community Management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
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
      </body>
    </html>
  );
}
