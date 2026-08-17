import type { ImpactRow } from "@/lib/types";

type Props = {
  rows: ImpactRow[];
};

export function ScenarioImpactTable({ rows }: Props) {
  return (
    <section className="impactTable">
      <div className="panelHeader">
        <h2>Scenario Impact</h2>
        <span>Baseline vs simulation</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>KPI</th>
            <th>Baseline</th>
            <th>Scenario</th>
            <th>Delta</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.kpi}>
              <td>{row.kpi}</td>
              <td>{row.baseline}</td>
              <td>{row.scenario}</td>
              <td>{row.delta}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

