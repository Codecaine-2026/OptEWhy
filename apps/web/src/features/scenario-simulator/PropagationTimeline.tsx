const steps = ["Intervention", "Yard", "Transport", "Quay", "Turnaround"];

export function PropagationTimeline() {
  return (
    <section className="timelinePanel">
      <div className="panelHeader">
        <h2>Propagation</h2>
        <span>4 steps</span>
      </div>
      <div className="timeline">
        {steps.map((step, index) => (
          <div key={step} className="timelineStep">
            <span>{index + 1}</span>
            <strong>{step}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

