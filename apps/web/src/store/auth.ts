import { create } from "zustand";

interface User {
  id: string;
  phone_number: string;
  role: string;
}

interface AuthState {
  token: string | null;
  tenantId: string | null;
  user: User | null;
  setAuth: (token: string, tenantId: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== "undefined" ? localStorage.getItem("token") : null,
  tenantId: typeof window !== "undefined" ? localStorage.getItem("tenantId") : null,
  user: null, // Would typically hydrate from localStorage or a /me endpoint

  setAuth: (token, tenantId, user) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("token", token);
      localStorage.setItem("tenantId", tenantId);
    }
    set({ token, tenantId, user });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("tenantId");
    }
    set({ token: null, tenantId: null, user: null });
  },
}));
