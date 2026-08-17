# FCM Modeling

The Dynamic FCM engine is the causal computation core.

Initial implementation scope:

- Static graph representation.
- Static propagation.
- Dominant path discovery.
- Feedback loop detection.
- Scenario state override.

Target model behavior:

```text
X(t + 1) = activation(X(t) * W(context_t))
```

The prototype can use static expert weights and regime-specific overrides. Later phases should introduce dynamic weight models that adjust edge weights based on yard density, vessel workload, equipment availability, time of day, weather, and traffic conditions.

The LLM must not calculate causal influence. It should only translate user input and explain backend-generated causal results.

