import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  timeout: 10000,
});

const TOKEN_KEY = "ecovision_token";

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setAuthToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuthToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

export async function register(fullName, email, password) {
  const { data } = await api.post("/auth/register", {
    full_name: fullName,
    email,
    password,
  });
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get("/auth/me");
  return data;
}

export async function fetchDashboard() {
  const { data } = await api.get("/dashboard");
  return data;
}

export async function uploadWasteImage(file, location) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("location", location);
  const { data } = await api.post("/predict", formData);
  return data;
}

export async function askQuery(query) {
  const { data } = await api.post("/query", { query });
  return data;
}

export async function sendSensorReading(payload) {
  const { data } = await api.post("/sensor", payload);
  return data;
}
