# sqlsmith

Natural-language-to-SQL as a service, with a **read-only safety layer** and an
**eval-gated CI** — a full-stack AI app where correctness is objectively
measurable (does the SQL return the right rows?).

![CI](https://github.com/MeghnaB12/sqlsmith/actions/workflows/ci.yml/badge.svg)

## Status (Week 1 vertical slice)

Working end to end today:

- `POST /v1/query` — question in → validated SQL (and rows) out
- **Safety layer** (`app/sql/safety.py`) — parses generated SQL with sqlglot and
  guarantees a single read-only query, rejecting stacked statements and any
  DML/DDL; auto-appends a `LIMIT` to bare selects
- **Sandbox** (`app/db/sandbox.py`) — a fresh in-memory DuckDB per request,
  seeded with a sample dataset, with schema introspection for prompt injection
- **Stub generator** so the whole pipeline runs and is tested with no API key

Example:

```bash
curl -X POST localhost:8000/v1/query \
  -H 'content-type: application/json' \
  -d '{"question": "list all customers"}'
# -> {"sql": "SELECT ... LIMIT 100", "rows": [...], "row_count": 4}
```

## What I build next (the actual work)

- [ ] **Real generator** — flesh out `AnthropicSQLGenerator`, iterate the prompt
      (schema formatting, few-shot examples, dialect hints)
- [ ] **Eval harness** — a labeled set (question → gold SQL → expected rows),
      scored by **execution accuracy**, seeded from Spider/WikiSQL
- [ ] **Eval-gated CI** — GitHub Action fails the build if accuracy drops below
      a threshold
- [ ] **Observability** — Langfuse tracing + token-cost logging per request
- [ ] **Frontend** — a minimal UI to try questions against the sandbox

## Run it

```bash
make install
make dev        # http://localhost:8000/docs
make check      # ruff + mypy + pytest
```

Point it at a real model by setting `GENERATOR_PROVIDER=anthropic` and
`ANTHROPIC_API_KEY=...` in `.env`.

## Design decisions

- **The model is untrusted.** Generated SQL is validated by an AST parser, not a
  regex or a "please only SELECT" prompt — prompts leak, parsers don't.
- **Ephemeral in-memory sandbox** rebuilt per request: even a query that slips
  past validation has nothing persistent to harm.
- **Generator behind a Protocol**, so the stub (CI, no key) and the real client
  are interchangeable and correctness work is isolated to one module.
