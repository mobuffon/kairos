"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Badge, EmptyState, SectionCard } from "@/components/SectionCard";
import {
  devLogin,
  getConnections,
  getProfileSummary,
  type ProfileSummary,
} from "@/lib/api";
import {
  configSummary,
  formatDate,
  formatRelativeDays,
  hobbyLabel,
} from "@/lib/format";

const DEV_USERS = ["mo", "anneka", "darian"] as const;

export default function DashboardPage() {
  const [userKey, setUserKey] = useState<string>("mo");
  const [profile, setProfile] = useState<ProfileSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = useCallback(async (key: string) => {
    setLoading(true);
    setError(null);
    try {
      const token = await devLogin(key);
      setProfile(await getProfileSummary(token));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load dashboard");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    getConnections().catch(() => {});
    loadProfile(userKey);
  }, [userKey, loadProfile]);

  const prefs = profile?.preferences;

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">
            Your living profile — contacts, calendar, hobbies, facts, and conversations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="user-select" className="text-sm font-medium text-slate-600">
            Dev user
          </label>
          <select
            id="user-select"
            value={userKey}
            onChange={(e) => setUserKey(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-kairos-500 focus:outline-none focus:ring-2 focus:ring-kairos-500/20"
          >
            {DEV_USERS.map((u) => (
              <option key={u} value={u}>
                {u}
              </option>
            ))}
          </select>
        </div>
      </div>

      {prefs && (
        <div className="flex flex-wrap gap-3 text-sm text-slate-600">
          <span className="rounded-full bg-white px-3 py-1 ring-1 ring-slate-200">
            @{prefs.telegram_username ?? profile?.user_key}
          </span>
          {prefs.location_label && (
            <span className="rounded-full bg-white px-3 py-1 ring-1 ring-slate-200">
              {prefs.location_label}
            </span>
          )}
          <span className="rounded-full bg-white px-3 py-1 ring-1 ring-slate-200">
            {prefs.timezone}
          </span>
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading && !profile && (
        <p className="text-sm text-slate-500">Loading profile…</p>
      )}

      {profile && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Calendar */}
          <SectionCard
            title="Calendar"
            description="Google Calendar connection"
            badge={
              profile.calendar.connected ? (
                <Badge variant="success">Connected ✓</Badge>
              ) : (
                <Badge variant="warning">Not connected</Badge>
              )
            }
          >
            <div className="space-y-3 text-sm">
              <p className="text-slate-600">
                Provider: <span className="font-medium capitalize">{profile.calendar.provider}</span>
                {profile.calendar.connected && (
                  <> · Sync {profile.calendar.sync_enabled ? "enabled" : "paused"}</>
                )}
              </p>
              {!profile.calendar.connected && (
                <Link
                  href="/settings"
                  className="inline-flex text-sm font-medium text-kairos-600 hover:text-kairos-700"
                >
                  Connect in Settings →
                </Link>
              )}
            </div>
          </SectionCard>

          {/* Upcoming suggestions */}
          <SectionCard
            title="Suggestions"
            description="Proactive activity windows"
            className="lg:col-span-2"
          >
            {profile.upcoming_suggestions.length === 0 ? (
              <EmptyState message="No matching windows right now — conditions or calendar don't align." />
            ) : (
              <ul className="divide-y divide-slate-100">
                {profile.upcoming_suggestions.map((s, i) => (
                  <li key={i} className="flex flex-col gap-1 py-3 first:pt-0 last:pb-0 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize text-slate-900">
                          {hobbyLabel(s.hobby_type)}
                        </span>
                        <Badge>{s.score.toFixed(2)}</Badge>
                      </div>
                      <p className="mt-1 text-sm text-slate-600">{s.message}</p>
                      <p className="mt-1 text-xs text-slate-400">{s.conditions}</p>
                    </div>
                    <time className="shrink-0 text-xs text-slate-500 sm:text-right">
                      {formatDate(s.window_start)}
                    </time>
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>

          {/* Contacts */}
          <SectionCard title="Contacts" description="People you track">
            {profile.contacts.length === 0 ? (
              <EmptyState message="No contacts yet — add them during onboarding or via Telegram." />
            ) : (
              <ul className="divide-y divide-slate-100">
                {profile.contacts.map((c) => (
                  <li key={c.name} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                    <div>
                      <p className="font-medium text-slate-900">{c.name}</p>
                      <p className="text-xs capitalize text-slate-500">
                        {c.relationship_type ?? "contact"} · every {c.contact_frequency_days}d
                      </p>
                    </div>
                    <span className="text-xs text-slate-500">
                      {formatRelativeDays(c.last_contacted_at)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>

          {/* Hobbies */}
          <SectionCard title="Hobbies" description="Enabled activities & thresholds">
            {profile.hobbies.filter((h) => h.enabled).length === 0 ? (
              <EmptyState message="No hobbies enabled." />
            ) : (
              <ul className="space-y-3">
                {profile.hobbies
                  .filter((h) => h.enabled)
                  .map((h) => (
                    <li
                      key={h.hobby_type}
                      className="rounded-lg bg-slate-50 px-3 py-2.5 ring-1 ring-slate-100"
                    >
                      <p className="font-medium capitalize text-slate-900">
                        {hobbyLabel(h.hobby_type)}
                      </p>
                      <p className="mt-0.5 text-xs text-slate-500">{configSummary(h.config)}</p>
                    </li>
                  ))}
              </ul>
            )}
          </SectionCard>

          {/* Profile facts */}
          <SectionCard title="Profile facts" description="Living profile (category · validity)">
            {profile.profile_facts.length === 0 ? (
              <EmptyState message="No facts learned yet — chat with Kairos to build your profile." />
            ) : (
              <ul className="divide-y divide-slate-100">
                {profile.profile_facts.map((f, i) => (
                  <li key={i} className="py-3 first:pt-0 last:pb-0">
                    <div className="flex items-center gap-2">
                      <Badge>{f.category}</Badge>
                      {f.valid_until && (
                        <span className="text-xs text-amber-600">
                          until {formatDate(f.valid_until)}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 text-sm text-slate-700">{f.fact}</p>
                    {f.source && (
                      <p className="mt-0.5 text-xs text-slate-400">via {f.source}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>

          {/* Conversations */}
          <SectionCard title="Conversations" description="Message history">
            {profile.conversations.length === 0 ? (
              <EmptyState message="No messages yet." />
            ) : (
              <ul className="max-h-72 space-y-3 overflow-y-auto pr-1">
                {[...profile.conversations]
                  .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                  .map((c, i) => (
                    <li
                      key={i}
                      className={`rounded-lg px-3 py-2 text-sm ${
                        c.direction === "inbound"
                          ? "bg-slate-100 text-slate-800"
                          : "bg-kairos-50 text-kairos-900"
                      }`}
                    >
                      <div className="mb-1 flex items-center justify-between text-xs text-slate-500">
                        <span className="capitalize">
                          {c.direction} · {c.channel}
                        </span>
                        <time>{formatDate(c.created_at)}</time>
                      </div>
                      <p>{c.message_text}</p>
                    </li>
                  ))}
              </ul>
            )}
          </SectionCard>

          {/* Suggestion history */}
          <SectionCard
            title="Suggestion history"
            description="Past proactive messages"
            className="lg:col-span-2"
          >
            {profile.suggestions.length === 0 ? (
              <EmptyState message="No suggestions sent yet." />
            ) : (
              <ul className="divide-y divide-slate-100">
                {profile.suggestions.map((s, i) => (
                  <li key={i} className="py-3 first:pt-0 last:pb-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium capitalize">{hobbyLabel(s.hobby_type)}</span>
                      {s.response && (
                        <Badge variant={s.response === "confirm" ? "success" : "default"}>
                          {s.response}
                        </Badge>
                      )}
                      {s.sent_at && (
                        <time className="text-xs text-slate-400">{formatDate(s.sent_at)}</time>
                      )}
                    </div>
                    <p className="mt-1 text-sm text-slate-600">{s.message_text}</p>
                    {s.conditions_summary && (
                      <p className="mt-0.5 text-xs text-slate-400">{s.conditions_summary}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>
        </div>
      )}

      <p className="text-center text-xs text-slate-400">
        <Link href="/dev/scenarios" className="hover:text-kairos-600">
          Run evaluation scenarios →
        </Link>
      </p>
    </div>
  );
}
