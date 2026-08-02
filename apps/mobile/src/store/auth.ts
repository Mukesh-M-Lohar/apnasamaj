import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  tenantId: string | null;
  user: any | null;
  
  login: (token: string, tenant: string, userData: any) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  accessToken: null,
  tenantId: null,
  user: null,

  login: async (token, tenant, userData) => {
    await SecureStore.setItemAsync('access_token', token);
    await SecureStore.setItemAsync('tenant_id', tenant);
    // Ideally, we'd stringify user data or just fetch it later
    
    set({
      isAuthenticated: true,
      accessToken: token,
      tenantId: tenant,
      user: userData,
    });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('tenant_id');
    
    set({
      isAuthenticated: false,
      accessToken: null,
      tenantId: null,
      user: null,
    });
  },

  checkAuth: async () => {
    const token = await SecureStore.getItemAsync('access_token');
    const tenant = await SecureStore.getItemAsync('tenant_id');
    
    if (token && tenant) {
      set({
        isAuthenticated: true,
        accessToken: token,
        tenantId: tenant,
      });
    } else {
      set({ isAuthenticated: false });
    }
  },
}));
