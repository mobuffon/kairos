"use client";

import { useEffect, useState } from "react";

import { Badge, SectionCard } from "@/components/SectionCard";
import {
  devLogin,
  getConnections,
  getGoogleOAuthUrl,
  getProfileSummary,
  getUserSettings,
  type UserPreferences,
} from "@/lib/api";
import { formatQuietHours } from "@/lib/format";

export default function SettingsPage() {
  const [userKey, setUserKey] = useState("mo");
  const [prefs, setPrefs] = useState<UserPreferences | null>(null);
  const [calendarUrl, setCalendarUrl] = useState<string | null>(null);
  const [calendarNote, setCalendarNote] = useState<string | null>(null);
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [devUsers, setDevUsers] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [oauth, connections] = await Promise.all([
          getGoogleOAuthUrl(),
          getConnections(),
        ]);
        setCalendarUrl(oauth.url);
        setCalendarNote(
          oauth.message ?? (oauth.mock === "true" ? "Mock calendar mode" : null),
        );
        setDevUsers(connections.users);

        const token = await devLogin(userKey);
        const [settings, summary] = await Promise.all([
          getUserSettings(token),
          getProfileSummary(token),
        ]);
        setPrefs(settings);
        setCalendarConnected(summary.calendar.connected);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load settings");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userKey]);

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Settings</h1>
        <p className="mt-1 text-sm text-slate-500">
          Tool connections and preferences stored on your user record.
        </p>
      </div>

      <div className="flex items-center gap-2">
        <label htmlFor="settings-user" className="text-sm font-medium text-slate-600">
          Dev user
        </label>
        <select
          id="settings-user"
          value={userKey}
          onChange={(e) => setUserKey(e.target.value)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-kairos-500 focus:outline-none focus:ring-2 focus:ring-kairos-500/20"
        >
          {devUsers.map((u) => (
            <option key={u} value={u}>
              {u}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading && <p className="text-sm text-slate-500">Loading…</p>}

      {!loading && (
        <div className="space-y-6">
          <SectionCard
            title="Google Calendar"
            description="Read free/busy for suggestion windows"
            badge={
              calendarConnected ? (
                <Badge variant="success">Connected ✓</Badge>
              ) : (
                <Badge variant="warning">Not connected</Badge>
              )
            }
          >
            <div className="space-y-3 text-sm">
              {calendarNote && <p className="text-slate-500">{calendarNote}</p>}
              {!calendarConnected && calendarUrl && (
                <a
                  href={calendarUrl}
                  className="inline-flex items-center rounded-lg bg-kairos-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-kairos-700"
                >
                  Link Google Calendar
                </a>
              )}
              {calendarConnected && (
                <p className="text-slate-600">
                  Calendar is linked. Kairos reads your free slots to find suggestion windows.
                </p>
              )}
            </div>
          </SectionCard>

          <SectionCard title="Telegram" description="Primary messaging channel">
            <div className="space-y-2 text-sm text-slate-600">
              {prefs?.telegram_username ? (
                <>
                  <p>
                    Connected as{" "}
                    <span className="font-medium text-slate-900">
                      @{prefs.telegram_username}
                    </span>
                  </p>
                  <Badge variant="success">Connected ✓</Badge>
                </>
              ) : (
                <p>Link your Telegram account via the bot to receive suggestions.</p>
              )}
            </div>
          </SectionCard>

          <SectionCard title="Preferences" description="Fields on the users table">
            {prefs ? (
              <dl className="grid gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Timezone
                  </dt>
                  <dd className="mt-1 text-sm font-medium text-slate-900">{prefs.timezone}</dd>
                </div>
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Location
                  </dt>
                  <dd className="mt-1 text-sm font-medium text-slate-900">
                    {prefs.location_label ?? "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Quiet hours
                  </dt>
                  <dd className="mt-1 text-sm font-medium text-slate-900">
                    {formatQuietHours(prefs.quiet_hours_start, prefs.quiet_hours_end)}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Max suggestions / day
                  </dt>
                  <dd className="mt-1 text-sm font-medium text-slate-900">
                    {prefs.max_suggestions_per_day}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Check-in frequency
                  </dt>
                  <dd className="mt-1 text-sm font-medium text-slate-900">
                    Every {prefs.check_in_frequency_days} days
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="text-sm text-slate-500">Could not load preferences.</p>
            )}
            <p className="mt-4 text-xs text-slate-400">
              Editing preferences via the UI is coming soon — values are read from your user record.
            </p>
          </SectionCard>
        </div>
      )}
    </div>
  );
}
