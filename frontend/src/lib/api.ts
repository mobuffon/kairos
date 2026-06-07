const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Suggestion = {
  hobby_type: string;
  score: number;
  window_start: string;
  window_end: string;
  conditions: string;
  message: string;
};

export async function devLogin(user: string): Promise<string> {
  const res = await fetch(`${API_URL}/auth/dev-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user }),
  });
  if (!res.ok) throw new Error("Login failed");
  const data = await res.json();
  return data.access_token as string;
}

export async function evaluateUser(token: string, scenario?: string): Promise<Suggestion[]> {
  const url = new URL(`${API_URL}/tools/evaluate`);
  if (scenario) url.searchParams.set("scenario", scenario);
  const res = await fetch(url.toString(), {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Evaluate failed");
  const data = await res.json();
  return data.suggestions as Suggestion[];
}

export async function healthCheck(): Promise<Record<string, string>> {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}
