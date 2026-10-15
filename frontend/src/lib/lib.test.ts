import { describe, expect, it } from "vitest";

import { toCsv } from "./csv";
import { formatDate, formatInt, formatPct } from "./format";

describe("toCsv", () => {
  it("keeps column order and escapes commas, quotes and newlines", () => {
    const csv = toCsv(["id", "note", "n"], [
      { id: "A", note: 'says "hi", twice', n: 1 },
      { id: "B", note: "line1\nline2", n: null },
    ]);
    expect(csv).toBe('id,note,n\nA,"says ""hi"", twice",1\nB,"line1\nline2",\n');
  });
});

describe("format helpers", () => {
  it("formats integers, percentages and dates", () => {
    expect(formatInt(7043)).toBe("7,043");
    expect(formatPct(0.2654)).toBe("26.5%");
    expect(formatPct(0.2, 0)).toBe("20%");
    expect(formatDate("2026-10-15T08:00:00")).toBe("15 Oct 2026");
    expect(formatDate("not a date")).toBe("not a date");
  });
});
