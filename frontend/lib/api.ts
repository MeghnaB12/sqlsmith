const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type AuthResponse = {
  access_token: string;
  token_type: string;
  email: string;
};

export type QueryResponse = {
  sql: string;
  rows: Array<Record<string, unknown>>;
  row_count: number;
};

export type HistoryItem = {
  id: number;
  question: string;
  sql: string;
  executed: boolean;
  row_count: number;
  created_at: string;
};

async function jsonRequest<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });

  const body = await response.json();
  if (!response.ok) {
    const message = typeof body?.detail === "string" ? body.detail : "Request failed";
    throw new Error(message);
  }
  return body as T;
}

export function authenticate(
  mode: "register" | "login",
  email: string,
  password: string,
): Promise<AuthResponse> {
  return jsonRequest<AuthResponse>(`/v1/auth/${mode}`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function runQuery(token: string, question: string): Promise<QueryResponse> {
  return jsonRequest<QueryResponse>("/v1/query", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ question, execute: true }),
  });
}

export function loadHistory(token: string): Promise<HistoryItem[]> {
  return jsonRequest<HistoryItem[]>("/v1/history", {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
}
