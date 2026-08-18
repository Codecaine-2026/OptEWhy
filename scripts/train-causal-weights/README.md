# Train Causal Weights

This script demonstrates how to estimate static FCM edge weights from the synthetic current-state and next-state observations for the shared eight-node port graph.

Run it from the repository root:

```bash
make train-causal
```

The trainer:

1. Loads `data/synthetic/sample_causal_training.csv`.
2. Excludes rows containing explicit interventions from ordinary fitting.
3. Derives the graph topology from `causal_engine.port_graph` and learns all twelve edge weights using inverse-`tanh` ridge regression.
4. Constrains weights to the FCM range `[-1, 1]`.
5. Writes `data/synthetic/trained_causal_model.json` with learned weights, RMSE metrics, and error against the hidden synthetic weights.

The default dataset contains 900 observational rows and 100 controlled-intervention rows. Its output demonstrates the training mechanism and should not be treated as operationally validated.
