"use client";

import { useEffect, useState } from "react";

import {
  devLogin,
  evaluateUser,
  getConnections,
  runSelftest,
  type SelftestResponse,
  type Suggestion,
} from "@/lib/api";

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [selected, setSelected] = useState("mo_surf_perfect");
  const [user, setUser] = useState("mo");
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selftest, setSelftest] = useState<SelftestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getConnections()
      .then((c) => setScenarios(c.scenarios))
      .catch((e) => setError(e instanceof Error ? e.message : "Load failed"));
  }, []);

  async function runEvaluate() {
    setLoading(true);
    setError(null);
    try {
      const token = await devLogin(user);
      setSuggestions(await evaluateUser(token, selected));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Evaluate failed");
    } finally {
      setLoading(false);
    }
  }

  async function runAllSelftests() {
    setLoading(true);
    setError(null);
    try {
      setSelftest(await runSelftest());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Selftest failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Dev — Scenarios</h1>
      <p>Run mock evaluation scenarios against the suggestion engine.</p>

      <div style={{ marginBottom: "1rem" }}>
        <label>
          User{" "}
          <select value={user} onChange={(e) => setUser(e.target.value)}>
            <option value="mo">mo</option>
            <option value="anneka">anneka</option>
            <option value="darian">darian</option>
          </select>
        </label>{" "}
        <label>
          Scenario{" "}
          <select value={selected} onChange={(e) => setSelected(e.target.value)}>
            {scenarios.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>{" "}
        <button onClick={runEvaluate} disabled={loading}>
          Evaluate
        </button>{" "}
        <button onClick={runAllSelftests} disabled={loading}>
          Run all selftests
        </button>
      </div>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {suggestions.length > 0 && (
        <>
          <h2>Suggestions</h2>
          <ul>
            {suggestions.map((s, i) => (
              <li key={i}>
                <strong>{s.hobby_type}</strong> ({s.score.toFixed(2)}) — {s.message}
              </li>
            ))}
          </ul>
        </>
      )}

      {selftest && (
        <>
          <h2>
            Selftest: {selftest.passed}/{selftest.total}{" "}
            {selftest.all_passed ? "✓" : "✗"}
          </h2>
          <ul>
            {selftest.results.map((r) => (
              <li key={r.id} style={{ color: r.passed ? "green" : "crimson" }}>
                {r.passed ? "PASS" : "FAIL"} {r.id}: {r.message}
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  );
}
