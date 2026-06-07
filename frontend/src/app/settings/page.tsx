"use client";

import { useEffect, useState } from "react";

import { devLogin, getGoogleOAuthUrl, getConnections } from "@/lib/api";

export default function SettingsPage() {
  const [calendarUrl, setCalendarUrl] = useState<string | null>(null);
  const [calendarNote, setCalendarNote] = useState<string | null>(null);
  const [users, setUsers] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const oauth = await getGoogleOAuthUrl();
        setCalendarUrl(oauth.url);
        setCalendarNote(oauth.message ?? (oauth.mock === "true" ? "Mock calendar mode" : null));
        const connections = await getConnections();
        setUsers(connections.users);
        await devLogin("mo");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load settings");
      }
    }
    load();
  }, []);

  return (
    <main>
      <h1>Settings</h1>
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <section style={{ marginBottom: "1.5rem" }}>
        <h2>Calendar</h2>
        {calendarNote && <p style={{ color: "#666" }}>{calendarNote}</p>}
        {calendarUrl && (
          <p>
            <a href={calendarUrl}>Link Google Calendar</a>
          </p>
        )}
      </section>

      <section style={{ marginBottom: "1.5rem" }}>
        <h2>Quiet hours</h2>
        <p>22:00 – 07:00 (default, editable via API soon)</p>
      </section>

      <section>
        <h2>Dev users</h2>
        <ul>
          {users.map((u) => (
            <li key={u}>{u}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
