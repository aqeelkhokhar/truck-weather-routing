import { describe, expect, it } from "vitest";
import { addHours, formatDuration, formatMiles, toLocalInputValue } from "./format";

describe("format", () => {
  it("formats durations with hours and minutes", () => {
    expect(formatDuration(61574)).toBe("17h 6m");
  });

  it("formats durations under an hour", () => {
    expect(formatDuration(1500)).toBe("25m");
  });

  it("formats miles with separators", () => {
    expect(formatMiles(1234.4)).toBe("1,234 mi");
  });

  it("adds hours to an ISO timestamp", () => {
    expect(addHours("2026-11-01T00:00:00.000Z", 6)).toBe("2026-11-01T06:00:00.000Z");
  });

  it("produces a datetime local value", () => {
    expect(toLocalInputValue(new Date(2026, 10, 1, 9, 5))).toBe("2026-11-01T09:05");
  });
});
