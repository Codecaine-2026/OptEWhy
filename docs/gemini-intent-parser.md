# Gemini Intent Parser

The API uses Gemini structured output to convert a natural-language port-operations request into
the existing `StructuredQuery` contract. Gemini classifies and extracts only; causal paths,
feedback loops, and scenario results remain the responsibility of the causal engine.

## Configuration

Gemini mode is the default. Copy the project environment template, set a Gemini Developer API key,
then start the API:

```bash
cp .env.example .env
```

```dotenv
INTENT_PARSER_MODE=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.6-flash
GEMINI_TIMEOUT_SECONDS=10
```

```bash
make api
```

`make api` loads the root `.env` file. The API key must never be placed in frontend environment
variables or committed to Git. Mock mode remains available for offline work with
`INTENT_PARSER_MODE=mock`.

`INTENT_PARSER_FALLBACK_TO_MOCK=true` enables deterministic fallback if Gemini is unavailable. It
is disabled by default so a production outage cannot silently change interpretation behavior.

## Request flow

1. FastAPI selects the configured parser.
2. `GeminiIntentParser` sends the message and active causal-node catalog to Gemini.
3. Gemini returns JSON constrained by the `IntentOutput` Pydantic schema.
4. The application validates the selected node against the active graph and preserves the original
   message.
5. The validated `StructuredQuery` is passed to the existing causal engine.

Unsupported model-selected nodes return HTTP 422. Gemini failures return HTTP 503 unless mock
fallback is explicitly enabled.

## Verification

Regular tests use fake clients and make no Gemini requests:

```bash
pytest
ruff check .
mypy apps/api/src packages/llm-orchestrator/src
```

The opt-in live parser test makes a paid API request:

```bash
RUN_GEMINI_LIVE_TEST=1 pytest packages/llm-orchestrator/tests/test_gemini_live.py
```
