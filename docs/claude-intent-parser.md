# Claude Intent Parser

The API uses Claude to convert a natural-language port-operations request into the existing
`StructuredQuery` contract. Claude classifies and extracts only; causal paths, feedback loops, and
scenario results remain the responsibility of the causal engine.

## Configuration

Claude mode is the default. Copy the project environment template, set an Anthropic API key, then
start the API:

```bash
cp .env.example .env
```

```dotenv
INTENT_PARSER_MODE=claude
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-haiku-4-5-20251001
CLAUDE_TIMEOUT_SECONDS=10
```

The API key must never be placed in frontend environment variables or committed to Git. Mock mode
remains available for offline work with `INTENT_PARSER_MODE=mock`.

`INTENT_PARSER_FALLBACK_TO_MOCK=true` enables deterministic fallback if Claude is unavailable. It
is disabled by default so a production outage cannot silently change interpretation behavior.

## Request flow

1. FastAPI selects the configured parser.
2. `ClaudeIntentParser` sends the message and active causal-node catalog to Claude.
3. Claude returns JSON for the `IntentOutput` Pydantic schema.
4. The application validates the selected node against the active graph and preserves the original
   message.
5. The validated `StructuredQuery` is passed to the existing causal engine.

Unsupported model-selected nodes return HTTP 422. Claude failures return HTTP 503 unless mock
fallback is explicitly enabled.
