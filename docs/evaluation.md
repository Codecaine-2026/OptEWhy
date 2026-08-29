# Evaluation
 
## Video MVP Evaluation Criteria
 
For the video demo MVP, the system is evaluated primarily on presentation fidelity, responsiveness, and deterministic reliability:
 
1. **End-to-End Latency**: < 1.0s response time from prompt submission to complete UI graph and table update.
2. **Visual Clarity & Readability**: High-contrast node status indicators, clear causal path highlighting, and readable typography at 1080p recording resolution.
3. **Deterministic Consistency**: 100% reproducible answers, causal percentages, and scenario simulation outputs across repeated runs.
4. **Evidence Grounding**: 100% of generated explanations provide at least one valid, clickable operational report citation.
5. **Zero Friction Setup**: Local environment starts with a single command (`make dev`) without requiring external cloud credentials or background databases.
 
## Long-Term Production Metrics
 
Technical metrics:
- One-step and multi-step KPI prediction error.
- Expert agreement on top causal paths.
- Predicted vs actual scenario outcome.
- Evidence precision and citation relevance.
- Structured query parsing accuracy.
 
Operational metrics:
- Reduced diagnosis time.
- Reduced vessel turnaround time.
- Reduced QC waiting time.
- Reduced internal truck delay.
- Improved yard balancing.
 
Guardrail metrics:
- Unsupported causal claim rate (< 1%).
- Invalid intervention rejection rate.
- Hallucinated entity rate (0%).
- Explicit uncertainty calibration.


