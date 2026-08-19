# OpenAI Intent Parser

The API can use OpenAI Structured Outputs to convert a natural-language port-operations request
into the existing `StructuredQuery` contract. The model performs classification and extraction
only. Causal paths, feedback loops, and scenario results remain the responsibility of the causal
engine.

## Configuration

OpenAI mode is the default for the application. Configure the backend with your API key before
starting FastAPI:

```bash
export INTENT_PARSER_MODE=openai
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-5.6-luna"
export OPENAI_REASONING_EFFORT="low"
export OPENAI_TIMEOUT_SECONDS=10
make api
```

The API key must never be placed in frontend environment variables or committed to Git. The OpenAI
Python SDK reads the key on the backend. The `.env.example` files contain placeholders only.

Mock mode remains available for offline tests by explicitly setting `INTENT_PARSER_MODE=mock`.

`INTENT_PARSER_FALLBACK_TO_MOCK=true` enables deterministic fallback if the OpenAI request fails.
It is disabled by default so a production outage cannot silently change interpretation behavior.

## Request flow

1. FastAPI selects the configured parser.
2. `OpenAIIntentParser` sends the message and the active causal-node catalog to the Responses API.
3. Structured Outputs validates the response against `OpenAIIntentOutput`.
4. The application checks the selected node against the active graph and preserves the original
   message itself.
5. The validated `StructuredQuery` is passed to the existing causal engine.

Unsupported model-selected nodes return HTTP 422. OpenAI failures return HTTP 503 unless mock
fallback is explicitly enabled.

## Verification

Regular tests use fake clients and do not call OpenAI:

```bash
pytest
ruff check .
mypy apps/api/src packages/llm-orchestrator/src
```

The opt-in live parser test makes a paid API request:

```bash
RUN_OPENAI_LIVE_TEST=1 pytest packages/llm-orchestrator/tests/test_openai_live.py
```

For a live smoke test, start the API with OpenAI mode enabled and call:

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"message":"What is driving vessel turnaround time?","terminalId":"terminal_alpha"}'
```
