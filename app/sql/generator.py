"""SQL generators.

Handlers depend on the ``SQLGenerator`` Protocol, never a concrete provider.
``StubSQLGenerator`` keeps the service runnable and testable with no API key;
``AnthropicSQLGenerator`` is the real one you'll iterate on in Week 1-2.
"""

from typing import Protocol

_SYSTEM_PROMPT = """\
You translate a user's question into a single read-only SQL query for a DuckDB
database. Rules:
- Output ONLY the SQL. No prose, no markdown fences, no explanation.
- Use exactly one statement, and it must be a SELECT.
- Never modify data (no INSERT/UPDATE/DELETE/DDL).
- Only reference tables and columns present in the provided schema.

Schema:
{schema}
"""


class SQLGenerator(Protocol):
    """Turns a natural-language question + schema into a SQL string."""

    async def generate_sql(self, question: str, schema: str) -> str: ...


class StubSQLGenerator:
    """Deterministic generator for local runs, tests, and CI (no API key)."""

    async def generate_sql(self, question: str, schema: str) -> str:
        # A fixed, obviously-safe query. Real correctness comes from the
        # Anthropic generator; this only keeps the pipeline exercisable.
        return "SELECT name, country FROM customers ORDER BY name"


class AnthropicSQLGenerator:
    """Real generator. Fill in your key/model via settings, then tune the prompt.

    Left thin on purpose: the prompt engineering here is *your* Week 1-2 work
    and the thing you'll defend in interviews.
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def generate_sql(self, question: str, schema: str) -> str:
        # Lazy import so the dependency is only needed when this path is used.
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self._api_key)
        message = await client.messages.create(
            model=self._model,
            max_tokens=512,
            system=_SYSTEM_PROMPT.format(schema=schema),
            messages=[{"role": "user", "content": question}],
        )
        block = message.content[0]
        text = getattr(block, "text", "")
        return text.strip()
