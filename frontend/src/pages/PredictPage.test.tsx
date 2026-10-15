import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { apiError, callsTo, mockApi } from "@/test/mockApi";
import { renderApp } from "@/test/render";

describe("Predict Churn page", () => {
  it("sends the form to the API and shows the prediction", async () => {
    const fetchMock = mockApi();
    const { user } = renderApp("/predict");
    await user.click(await screen.findByRole("button", { name: /^Predict churn$/ }));

    expect(await screen.findByText("32.4%")).toBeInTheDocument();
    expect(screen.getByText("Likely to stay")).toBeInTheDocument();
    const [, init] = callsTo(fetchMock, "/api/predict")[0];
    const body = JSON.parse(String(init?.body));
    expect(body.customer).toMatchObject({ tenure: 12, Contract: "Month-to-month", TotalCharges: 780 });
    expect(body.threshold).toBe(0.36);
  });

  it("blocks submission and marks the field when input is invalid", async () => {
    const fetchMock = mockApi();
    const { user } = renderApp("/predict");
    const tenure = await screen.findByLabelText("Tenure (months)");
    await user.clear(tenure);
    await user.type(tenure, "-5");
    await user.click(screen.getByRole("button", { name: /^Predict churn$/ }));

    expect(tenure).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByText(/Must be between/)).toBeInTheDocument();
    expect(callsTo(fetchMock, "/api/predict")).toHaveLength(0);
  });

  it("shows the server's validation message when the API rejects the request", async () => {
    mockApi({ "POST /api/predict": () => apiError(422, "validation_error", "The customer record is invalid.", ["tenure: too large"]) });
    const { user } = renderApp("/predict");
    await user.click(await screen.findByRole("button", { name: /^Predict churn$/ }));
    expect(await screen.findByText("The customer record is invalid.")).toBeInTheDocument();
  });

  it("explains when the model is unavailable", async () => {
    mockApi({ "GET /api/schema": () => apiError(503, "model_unavailable", "No trained model was found.") });
    renderApp("/predict");
    expect(await screen.findByText("The model is not available")).toBeInTheDocument();
    expect(screen.getByText("No trained model was found.")).toBeInTheDocument();
  });
});
