# Generate Synthetic Causal Data

Generate deterministic transition data for the expanded reference port graph:

```bash
make generate-synthetic
```

The default dataset contains 2,400 rows, including normal baseline rows and eight
structural scenario families:

- `qc_productivity_down_yard_dwell_root`
- `qc_productivity_down_chassis_root`
- `qc_productivity_down_equipment_root`
- `truck_turn_time_up_document_root`
- `truck_turn_time_up_yard_retrieval_root`
- `vessel_turnaround_up_bunching_root`
- `yard_density_up_warehouse_root`
- `berth_productivity_down_yard_crane_root`

Each row includes current node values, intervention metadata, next node values, and
explicit explanation labels:

- `observed_kpi`
- `surface_cause_label`
- `root_cause_label`
- `reinforcing_loop_id`
- `recommended_intervention`
- `explanation_template`

The labels are designed for retrieval and explanation evaluation. They intentionally
include four repeated surface causes, each with multiple true upstream roots:

- `qc_waiting`: yard dwell, chassis shortage, or quay crane equipment availability
- `gate_congestion`: document exceptions, yard retrieval friction, or warehouse pickup failure
- `berth_occupancy`: vessel bunching, yard congestion/import dwell, or crane equipment
- `qc_productivity`: yard crane availability or quay crane equipment availability

The generator keeps normalized values roughly in `[-1, 1]` and uses:

```text
X(t+1) = tanh(X(t) + X(t)W + noise)
```

This dataset is synthetic. It demonstrates structural explanation patterns and weight
training mechanics, but it does not prove real terminal causality.
