# Generate Synthetic Causal Data

Generate deterministic transition data for the eight-node reference port graph:

```bash
make generate-synthetic
```

The default dataset contains 1,000 transitions across normal, congested, and weather-disruption regimes. Every tenth row contains a controlled yard-density or berth-occupancy intervention. The generator uses a fixed seed, the reference edge weights, Gaussian measurement noise, and the same state-transition equation as the causal engine:

```text
X(t+1) = tanh(X(t) + X(t)W + noise)
```

The generated dataset demonstrates weight recovery and scenario mechanics. It does not establish that the graph is valid for a real port.
