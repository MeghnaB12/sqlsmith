"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  authenticate,
  HistoryItem,
  loadHistory,
  QueryResponse,
  runQuery,
} from "../lib/api";

export default function HomePage() {
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("demo-password");
  const [token, setToken] = useState("");
  const [question, setQuestion] = useState("list all customers");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const saved = window.localStorage.getItem("sqlsmith_token");
    if (saved) setToken(saved);
  }, []);

  useEffect(() => {
    if (!token) return;
    loadHistory(token).then(setHistory).catch(() => {
      window.localStorage.removeItem("sqlsmith_token");
      setToken("");
    });
  }, [token]);

  async function handleAuth(mode: "register" | "login") {
    setBusy(true);
    setMessage("");
    try {
      const response = await authenticate(mode, email, password);
      window.localStorage.setItem("sqlsmith_token", response.access_token);
      setToken(response.access_token);
      setMessage(mode === "register" ? "Account created." : "Signed in.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleQuery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setMessage("Sign in before running a query.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const response = await runQuery(token, question);
      setResult(response);
      setHistory(await loadHistory(token));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Query failed");
    } finally {
      setBusy(false);
    }
  }

  function signOut() {
    window.localStorage.removeItem("sqlsmith_token");
    setToken("");
    setResult(null);
    setHistory([]);
    setMessage("Signed out.");
  }

  const columns = result?.rows.length ? Object.keys(result.rows[0]) : [];

  return (
    <main>
      <header className="hero">
        <div>
          <span className="eyebrow">SAFE AI DATA WORKSPACE</span>
          <h1>sqlsmith</h1>
          <p>
            Ask a question in plain English, inspect the validated SQL, execute it in an
            isolated sandbox, and keep a persistent history of your work.
          </p>
        </div>
        <div className="status">{token ? "Authenticated workspace" : "Sign in to query"}</div>
      </header>

      <section className="grid">
        <aside className="card auth-card">
          <div className="section-heading">
            <div>
              <span className="eyebrow">ACCOUNT</span>
              <h2>{token ? "Workspace access" : "Sign in or register"}</h2>
            </div>
          </div>

          {token ? (
            <>
              <p className="muted">Your query history is stored against this authenticated account.</p>
              <button className="secondary" onClick={signOut}>Sign out</button>
            </>
          ) : (
            <div className="stack">
              <label>
                Email
                <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
              </label>
              <label>
                Password
                <input
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  type="password"
                />
              </label>
              <div className="button-row">
                <button disabled={busy} onClick={() => handleAuth("login")}>Sign in</button>
                <button className="secondary" disabled={busy} onClick={() => handleAuth("register")}>Register</button>
              </div>
            </div>
          )}
        </aside>

        <section className="card query-card">
          <div className="section-heading">
            <div>
              <span className="eyebrow">QUERY</span>
              <h2>Ask the sandbox</h2>
            </div>
            <span className="pill">AST-validated read-only SQL</span>
          </div>
          <form onSubmit={handleQuery} className="stack">
            <textarea
              rows={4}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="e.g. show customers ordered by total spend"
            />
            <button disabled={busy || !token} type="submit">
              {busy ? "Working…" : "Generate and run SQL"}
            </button>
          </form>
          {message && <p className="message">{message}</p>}
        </section>
      </section>

      {result && (
        <section className="card result-card">
          <div className="section-heading">
            <div>
              <span className="eyebrow">RESULT</span>
              <h2>Validated SQL</h2>
            </div>
            <span className="pill">{result.row_count} rows</span>
          </div>
          <pre>{result.sql}</pre>
          {result.rows.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
                </thead>
                <tbody>
                  {result.rows.map((row, index) => (
                    <tr key={index}>
                      {columns.map((column) => <td key={column}>{String(row[column] ?? "")}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      <section className="card history-card">
        <div className="section-heading">
          <div>
            <span className="eyebrow">PERSISTENCE</span>
            <h2>Recent query history</h2>
          </div>
          <span className="pill">PostgreSQL-backed in Compose</span>
        </div>
        {history.length === 0 ? (
          <p className="muted">No saved queries yet.</p>
        ) : (
          <div className="history-list">
            {history.map((item) => (
              <article key={item.id}>
                <div>
                  <strong>{item.question}</strong>
                  <code>{item.sql}</code>
                </div>
                <span>{item.row_count} rows</span>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
