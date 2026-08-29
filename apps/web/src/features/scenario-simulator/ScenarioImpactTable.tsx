import type { ImpactRow } from "@/lib/types";

type Props = {
  rows: ImpactRow[];
  scenarioExplanation: string;
};

export function ScenarioImpactTable({ rows, scenarioExplanation }: Props) {
  return (
    <section className="impactTable">
      <div className="panelHeader">
        <h2>Scenario Impact</h2>
        <span>Chat-requested simulation</span>
      </div>
      <p className="scenarioStatus" role="status">{scenarioExplanation}</p>
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
