export function feedbackLoopLabel(loopType?: string | null) {
  switch (loopType?.trim().toLowerCase()) {
    case "reinforcing":
      return "Reinforcing loop";
    case "balancing":
      return "Balancing loop";
    default:
      return "Feedback loop";
  }
}
