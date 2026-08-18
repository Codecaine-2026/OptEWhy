# Reference Causal Graph

The executable reference graph models structural port causality across external demand,
landside gate flow, yard congestion, quay productivity, and vessel outcomes.

Key node groups:

- External and demand: `import_volume_pressure`, `vessel_bunching`, `weather_severity`
- Landside and gate: `gate_throughput`, `gate_queue_length`, `truck_arrival_peaking`,
  `truck_appointment_compliance`, `document_error_rate`, `gate_exception_rate`,
  `chassis_availability`, `warehouse_capacity_pressure`
- Yard: `import_dwell_time`, `yard_density`, `yard_rehandle_rate`,
  `yard_crane_availability`, `empty_container_imbalance`
- Quay and vessel: `berth_occupancy`, `truck_travel_time`, `qc_waiting`,
  `qc_productivity`, `crane_equipment_availability`, `labor_availability`,
  `berth_productivity`, `vessel_turnaround_time`

The graph keeps immediate KPI relationships, such as `qc_waiting -> qc_productivity`,
but it also includes upstream structural paths. For example, a low QC productivity case
can be explained as surface QC waiting while the true root cause is chassis shortage,
import dwell, yard density, and rehandles.

## Structural Loops

The graph includes a berth-yard-quay reinforcing loop:

```text
berth_occupancy -> yard_density -> truck_travel_time -> qc_waiting -> berth_occupancy
```

It also includes a landside-yard pickup loop:

```text
gate_throughput down -> import_dwell_time up -> yard_density up
-> truck_turn_time up -> gate_throughput down
```

These loops are structural hypotheses for explanation and scenario simulation. The
weights are synthetic ground truth for demonstration and training mechanics; they are
not calibrated proof of real terminal causality.
