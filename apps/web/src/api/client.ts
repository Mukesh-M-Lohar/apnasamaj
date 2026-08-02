import axios from "axios";

// Standard Base URL pointing to FastAPI
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Attach JWT and Tenant ID
apiClient.interceptors.request.use(
  (config) => {
    // We fetch these from localStorage in the browser
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      const tenantId = localStorage.getItem("tenantId");

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      if (tenantId) {
        config.headers["X-Tenant-ID"] = tenantId;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Global Response Interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Optionally redirect to login on 401
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
