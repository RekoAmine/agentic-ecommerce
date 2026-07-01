import { describe, expect, it } from "vitest";
import { scoreSegment } from "@/features/score/score";

describe("scoreSegment", () => {
  it.each([
    [86, "opportunité"],
    [74, "surveillance"],
    [51, "risque"]
  ] as const)("maps score %i to %s", (score, expected) => {
    expect(scoreSegment({ score })).toBe(expected);
  });
});
