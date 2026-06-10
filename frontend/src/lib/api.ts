const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Suggestion = {
  hobby_type: string;
  score: number;
  window_start: string;
  window_end: string;
  conditions: string;
  message: string;
};

export type Contact = {
  name: string;
  relationship_type?: string | null;
  contact_frequency_days: number;
  last_contacted_at?: string | null;
  notes?: string | null;
};

export type CalendarStatus = {
  connected: boolean;
  provider: string;
  sync_enabled: boolean;
  calendar_id: string;
};

export type Hobby = {
  hobby_type: string;
  enabled: boolean;
  config: Record<string, unknown>;
};

export type ProfileFact = {
  category: string;
  fact: string;
  valid_from?: string | null;
  valid_until?: string | null;
  source?: string | null;
};

export type Conversation = {
  direction: string;
  channel: string;
  message_text: string;
  created_at: string;
  extracted_facts?: Record<string, unknown> | null;
};

export type SuggestionHistory = {
  hobby_type: string;
  window_start: string;
  window_end: string;
  score: number;
  conditions_summary?: string | null;
  message_text?: string | null;
  sent_at?: string | null;
  response?: string | null;
};

export type UserPreferences = {
  timezone: string;
  location_label?: string | null;
  quiet_hours_start: number;
  quiet_hours_end: number;
  max_suggestions_per_day: number;
  check_in_frequency_days: number;
  telegram_username?: string | null;
};

export type ProfileSummary = {
  user_key: string;
  preferences: UserPreferences;
  contacts: Contact[];
  calendar: CalendarStatus;
  hobbies: Hobby[];
  profile_facts: ProfileFact[];
  conversations: Conversation[];
  suggestions: SuggestionHistory[];
  upcoming_suggestions: Suggestion[];
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

export async function getProfileSummary(token: string): Promise<ProfileSummary> {
  const res = await fetch(`${API_URL}/profile/summary`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to load profile");
  return res.json();
}

export async function getUserSettings(token: string): Promise<UserPreferences> {
  const res = await fetch(`${API_URL}/profile/settings`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to load settings");
  return res.json();
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

export type ConnectionInfo = {
  users: string[];
  scenarios: string[];
};

export type SelftestResult = {
  id: string;
  passed: boolean;
  message: string;
};

export type SelftestResponse = {
  passed: number;
  total: number;
  all_passed: boolean;
  results: SelftestResult[];
};

export async function getConnections(): Promise<ConnectionInfo> {
  const res = await fetch(`${API_URL}/tools/connections`);
  if (!res.ok) throw new Error("Failed to load connections");
  return res.json();
}

export async function runSelftest(): Promise<SelftestResponse> {
  const res = await fetch(`${API_URL}/tools/selftest`);
  if (!res.ok) throw new Error("Selftest failed");
  return res.json();
}

export async function getGoogleOAuthUrl(): Promise<{ url: string; mock?: string; message?: string }> {
  const res = await fetch(`${API_URL}/auth/google/url`);
  if (!res.ok) throw new Error("OAuth URL failed");
  return res.json();
}
