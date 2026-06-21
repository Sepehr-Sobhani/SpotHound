import type {
  ChatUpdate,
  CheckResult,
  EventItem,
  Spot,
  Subscriber,
  Target,
  TelegramStatus,
  User,
} from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "sh_token";

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  const t = tokenStore.get();
  if (t) headers["Authorization"] = `Bearer ${t}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    if (res.status === 401) tokenStore.clear();
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

function jsonBody(method: string, data: unknown): RequestInit {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  };
}

export const api = {
  async login(username: string, password: string): Promise<void> {
    const res = await fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
    });
    if (!res.ok) throw new Error("Incorrect username or password");
    const data = await res.json();
    tokenStore.set(data.access_token);
  },
  logout: () => tokenStore.clear(),

  me: () => request<User>("/users/me"),
  updateMe: (telegram_chat_id: string | null) =>
    request<User>("/users/me", jsonBody("PATCH", { telegram_chat_id })),
  testMyTelegram: () =>
    request<{ sent: boolean }>("/users/me/telegram/test", { method: "POST" }),

  telegramStatus: () => request<TelegramStatus>("/telegram/status"),
  telegramUpdates: () => request<ChatUpdate[]>("/telegram/updates"),

  listTargets: () => request<Target[]>("/targets"),
  listEvents: (id: number) => request<EventItem[]>(`/targets/${id}/events`),
  getTarget: (id: number) => request<Target>(`/targets/${id}`),
  updateTarget: (id: number, patch: Partial<Target>) =>
    request<Target>(`/targets/${id}`, jsonBody("PATCH", patch)),
  toggleTarget: (id: number) =>
    request<Target>(`/targets/${id}/toggle`, { method: "POST" }),
  testTarget: (id: number) =>
    request<CheckResult>(`/targets/${id}/test`, { method: "POST" }),

  listSubscribers: (id: number) =>
    request<Subscriber[]>(`/targets/${id}/subscribers`),
  subscribeUser: (id: number, userId: number) =>
    request<void>(`/targets/${id}/subscribers/${userId}`, { method: "POST" }),
  unsubscribeUser: (id: number, userId: number) =>
    request<void>(`/targets/${id}/subscribers/${userId}`, { method: "DELETE" }),

  listUsers: () => request<User[]>("/users"),
  createUser: (payload: {
    username: string;
    password: string;
    role: string;
    telegram_chat_id: string | null;
  }) => request<User>("/users", jsonBody("POST", payload)),

  listSpots: () => request<Spot[]>("/admin/spots"),
  syncSpots: () =>
    request<{ created: number; updated: number }>("/admin/sync-spots", {
      method: "POST",
    }),
};
