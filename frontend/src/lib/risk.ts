import type { DecidedBy, RiskLevel } from "../api/types";

export const RISK_ORDER: RiskLevel[] = ["LOW", "MODERATE", "HIGH", "SEVERE", "NO_TRAVEL"];

export const RISK_COLORS: Record<RiskLevel, string> = {
  LOW: "#2e7d32",
  MODERATE: "#f9a825",
  HIGH: "#ef6c00",
  SEVERE: "#c62828",
  NO_TRAVEL: "#4a148c",
};

export const RISK_LABELS: Record<RiskLevel, string> = {
  LOW: "Low",
  MODERATE: "Moderate",
  HIGH: "High",
  SEVERE: "Severe",
  NO_TRAVEL: "No travel",
};

export const HEAT_GRADIENT: Record<number, string> = {
  0.25: RISK_COLORS.LOW,
  0.5: RISK_COLORS.MODERATE,
  0.75: RISK_COLORS.HIGH,
  1: RISK_COLORS.SEVERE,
};

export const DECISION_REASONS: Record<DecidedBy, string> = {
  no_travel: "The other routes cross a no travel checkpoint.",
  severe_miles: "It has the fewest severe weather miles.",
  high_miles: "Severe miles tie, and it has the fewest high risk miles.",
  average_risk: "Severe and high miles tie, and it has the lowest average risk.",
  travel_time: "Weather risk ties, and it is the quickest.",
  tie: "All routes score the same on weather and time.",
  only_route: "It is the only route available.",
};

export function riskFromIndex(index: number): RiskLevel {
  return RISK_ORDER[Math.min(Math.max(Math.round(index), 0), RISK_ORDER.length - 1)] ?? "LOW";
}
