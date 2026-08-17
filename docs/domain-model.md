# Domain Model

The platform models a port as a hierarchy of operational subsystems:

- Vessel Operations.
- Berth Operations.
- Quay Operations.
- Yard Operations.
- Internal Transport.
- Gate Operations.
- Equipment.
- Labor.

The first prototype should focus on a single terminal, one vessel operation use case, and three connected subsystems: Quay, Yard, and Internal Transport.

Core entities:

- Terminal.
- Vessel.
- Berth.
- Quay Crane.
- Yard Block.
- Internal Truck.
- Gate.
- Equipment.
- Shift.

All operational metrics should be normalized before they are passed into the FCM engine. A normalized node value of `0` means baseline behavior, positive values mean above baseline, and negative values mean below baseline.

