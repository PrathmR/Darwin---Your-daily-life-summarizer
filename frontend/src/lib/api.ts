// frontend/src/lib/api.ts:
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
    ? `${import.meta.env.VITE_BACKEND_URL}/api`
    : "http://localhost:8000/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});
