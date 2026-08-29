import { AlertTriangle, ArrowDownRight, ArrowUpRight, CheckCircle2 } from "lucide-react";
import type { ImpactRow } from "@/lib/types";

type Props = {
  rows: ImpactRow[];
  scenarioMode?: boolean;
};

export function ScenarioImpactTable({ rows, scenarioMode = false }: Props) {
  return (
    <section className={`impactTable ${scenarioMode ? "impactTableActive" : ""}`}>
      <div className="panelHeader">
        <div className="impactTitleGroup">
          <h2>Scenario Impact</h2>
          <span className="impactSubhead">
            {scenarioMode
              ? "Simulated Intervention vs Operational Baseline"
              : "Operational Baseline (Awaiting Simulation)"}
          </span>
        </div>
        <div className="impactModeBadgeContainer">
          {scenarioMode ? (
            <span className="impactStatusBadge active">
              <CheckCircle2 size={13} />
              Simulated Intervention Active
            </span>
          ) : (
            <span className="impactStatusBadge idle">Baseline State</span>
          )}
        </div>
      </div>

      <div className="tableResponsiveWrapper">
        <table className="impactDataTable">
          <thead>
            <tr>
              <th>KPI</th>
              <th>Baseline</th>
              <th>Scenario</th>
              <th>Delta</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const isWarning = row.type === "warning";

              return (
                <tr
                  key={row.kpi}
                  className={scenarioMode ? (isWarning ? "impactRowWarning" : "impactRowImprovement") : ""}
                >
                  <td className="kpiCell">
                    <span className="kpiName">{row.kpi}</span>
                    {row.description && scenarioMode && (
                      <span className="kpiDescription">{row.description}</span>
                    )}
                  </td>
                  <td className="baselineCell">{row.baseline}</td>
                  <td className="scenarioCell">
                    {scenarioMode ? (
                      <span className="scenarioValueHighlight">{row.scenario}</span>
                    ) : (
                      <span className="scenarioValueInactive">—</span>
                    )}
                  </td>
                  <td className="deltaCell">
                    {scenarioMode ? (
                      isWarning ? (
                        <span className="deltaBadge deltaBadgeWarning">
                          <AlertTriangle size={12} />
                          {row.delta}
                        </span>
                      ) : (
                        <span className="deltaBadge deltaBadgeImprovement">
                          {row.delta.startsWith("+") ? (
                            <ArrowUpRight size={13} />
                          ) : (
                            <ArrowDownRight size={13} />
                          )}
                          {row.delta}
                        </span>
                      )
                    ) : (
                      <span className="deltaBadge deltaBadgeBaseline">Baseline</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {scenarioMode && (
        <div className="tradeoffAlertBanner">
          <AlertTriangle size={15} className="tradeoffAlertIcon" />
          <span>
            <strong>Tradeoff Notice:</strong> Block D density increase introduces a <strong>+2.0%</strong> gate retrieval delay during peak hours.
          </span>
        </div>
      )}
    </section>
  );
}

