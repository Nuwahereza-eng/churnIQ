import { describe, expect, it } from "vitest";

import { fixtures } from "@/test/mockApi";
import type { ModelSchema } from "@/types/api";

import { applyDependencies, DEFAULT_VALUES, estimatedTotal, validate } from "./validation";

const schema = fixtures.schema as unknown as ModelSchema;

describe("validate", () => {
  it("accepts the default values and builds a typed payload", () => {
    const { errors, payload } = validate(DEFAULT_VALUES, schema);
    expect(errors).toEqual({});
    expect(payload).toMatchObject({ tenure: 12, MonthlyCharges: 65, TotalCharges: 780, SeniorCitizen: 0 });
  });

  it("rejects missing, fractional and negative tenure", () => {
    expect(validate({ ...DEFAULT_VALUES, tenure: "" }, schema).errors.tenure).toMatch(/number of months/);
    expect(validate({ ...DEFAULT_VALUES, tenure: "2.5" }, schema).errors.tenure).toMatch(/whole number/);
    expect(validate({ ...DEFAULT_VALUES, tenure: "-1" }, schema).errors.tenure).toMatch(/between/);
  });

  it("rejects non-numeric charges and unknown categories", () => {
    const { errors, payload } = validate({ ...DEFAULT_VALUES, MonthlyCharges: "abc", Contract: "Lifetime" }, schema);
    expect(payload).toBeNull();
    expect(errors.MonthlyCharges).toBe("Enter a number.");
    expect(errors.Contract).toMatch(/listed options/);
  });

  it("requires manual total charges unless tenure is 0", () => {
    const manual = { ...DEFAULT_VALUES, autoTotal: false, TotalCharges: "" };
    expect(validate(manual, schema).errors.TotalCharges).toBeDefined();
    expect(validate({ ...manual, tenure: "0" }, schema).payload?.TotalCharges).toBeNull();
  });
});

describe("form helpers", () => {
  it("estimates total charges as tenure × monthly", () => {
    expect(estimatedTotal({ ...DEFAULT_VALUES, tenure: "3", MonthlyCharges: "19.99" })).toBe(59.97);
    expect(estimatedTotal({ ...DEFAULT_VALUES, tenure: "" })).toBeNull();
  });

  it("keeps add-on services consistent with their parent service", () => {
    const noInternet = applyDependencies({ ...DEFAULT_VALUES, InternetService: "No", PhoneService: "No" });
    expect(noInternet.OnlineSecurity).toBe("No internet service");
    expect(noInternet.TechSupport).toBe("No internet service");
    expect(noInternet.MultipleLines).toBe("No phone service");
    const back = applyDependencies({ ...noInternet, InternetService: "DSL", PhoneService: "Yes" });
    expect(back.OnlineSecurity).toBe("No");
    expect(back.MultipleLines).toBe("No");
  });
});
