import { describe, expect, it } from "vitest";
import { DECISION_REASONS, RISK_COLORS, RISK_ORDER, riskFromIndex } from "./risk";

describe("risk", () => {
  it("maps rounded averages to levels", () => {
    expect(riskFromIndex(0.2)).toBe("LOW");
    expect(riskFromIndex(1.6)).toBe("HIGH");
    expect(riskFromIndex(9)).toBe("NO_TRAVEL");
    expect(riskFromIndex(-3)).toBe("LOW");
  });

  it("has a color for every level", () => {
    RISK_ORDER.forEach((level) => expect(RISK_COLORS[level]).toMatch(/^#/));
  });

  it("explains every decisive criterion", () => {
    expect(Object.keys(DECISION_REASONS)).toHaveLength(7);
  });
});
