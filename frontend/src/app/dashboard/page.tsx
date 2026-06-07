"use client";

import { useEffect, useState } from "react";

import { devLogin, evaluateUser, healthCheck, type Suggestion } from "@/lib/api";

export default function DashboardPage() {
  const [health, setHealth] = useState<Record<string, string> | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setHealth(await healthCheck());
        const token = await devLogin("mo");
        setSuggestions(await evaluateUser(token, "mo_surf_perfect"));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
      }
    }
    load();
  }, []);

  return (
    <main>
      <h1>Dashboard</h1>
      {health && (
        <p>
          API: {health.status} (db: {health.db}, redis: {health.redis})
        </p>
      )}
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      <p>
        <a href="/dev/scenarios">Run more scenarios →</a>
      </p>
      <h2>Suggestions (Mo — mock surf scenario)</h2>
      <ul>
        {suggestions.map((s, i) => (
          <li key={i}>
            <strong>{s.hobby_type}</strong> ({s.score.toFixed(2)}) — {s.message}
          </li>
        ))}
      </ul>
    </main>
  );
}
