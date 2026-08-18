# Reference Causal Graph

The executable prototype graph contains eight nodes and twelve directed edges.

```mermaid
flowchart LR
    W[Weather Severity]
    A[Vessel Arrival Delay]
    B[Berth Occupancy]
    Y[Yard Density]
    T[Truck Travel Time]
    QW[QC Waiting]
    QP[QC Productivity]
    VT[Vessel Turnaround Time]

    W -->|+0.24| T
    W -->|-0.18| QP
    W -->|+0.22| VT
    A -->|+0.30| QW
    B -->|+0.42| Y
    B -->|+0.34| VT
    Y -->|+0.58| T
    T -->|+0.55| QW
    QW -->|-0.62| QP
    QW -->|+0.28| B
    QW -->|+0.36| VT
    QP -->|-0.52| VT
```

The positive cycle below represents a reinforcing congestion loop:

```text
QC Waiting
→ Berth Occupancy
→ Yard Density
→ Truck Travel Time
→ QC Waiting
```

Weather severity and vessel arrival delay are external context nodes. Vessel turnaround time is the broad outcome KPI; QC productivity remains an intermediate performance KPI.

The weights are synthetic ground truth for demonstrating propagation and weight recovery. They are not calibrated for a real terminal.
