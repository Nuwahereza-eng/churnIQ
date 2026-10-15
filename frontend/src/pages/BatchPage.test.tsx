import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { callsTo, fixtures, json, mockApi } from "@/test/mockApi";
import { renderApp } from "@/test/render";

import batchCsv from "@/test/fixtures/batch_small.csv?raw";
import invalidValidation from "@/test/fixtures/batch_validate_invalid.json";

const csvFile = (name = "customers.csv", content = batchCsv) => new File([content], name, { type: "text/csv" });

describe("Batch Predictions page", () => {
  it("validates an uploaded file, scores it and shows the results", async () => {
    const fetchMock = mockApi();
    const { user } = renderApp("/batch");
    await user.upload(await screen.findByLabelText("Customer CSV file"), csvFile());

    expect(await screen.findByText("Valid")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Run predictions for 5 records/ }));

    expect(await screen.findByRole("button", { name: /Download CSV/ })).toBeInTheDocument();
    expect(screen.getByText("Scored 5 records")).toBeInTheDocument();
    const processed = screen.getByText("Records processed").parentElement?.parentElement;
    expect(processed).toHaveTextContent(`Records processed${fixtures.batchPredict.n_records}`);
    expect(screen.getAllByText("8879-ZKJOF").length).toBeGreaterThan(0);
    expect(callsTo(fetchMock, "/api/predict/batch/validate")).toHaveLength(1);
    expect(callsTo(fetchMock, "/api/predict/batch")).toHaveLength(1);
  });

  it("lists row errors and disables scoring for an invalid file", async () => {
    mockApi({ "POST /api/predict/batch/validate": () => json(invalidValidation) });
    const { user } = renderApp("/batch");
    await user.upload(await screen.findByLabelText("Customer CSV file"), csvFile());

    expect(await screen.findByText("Invalid")).toBeInTheDocument();
    expect(screen.getByText(/'Contract' has invalid value 'Lifetime'/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Run predictions/ })).toBeDisabled();
  });

  it("rejects non-CSV and empty files before contacting the API", async () => {
    const fetchMock = mockApi();
    const { user } = renderApp("/batch");
    const input = await screen.findByLabelText("Customer CSV file");

    await user.upload(input, new File(["x"], "customers.xlsx"));
    expect(await screen.findByText("Please choose a .csv file.")).toBeInTheDocument();
    await user.upload(input, csvFile("empty.csv", ""));
    expect(await screen.findByText("The selected file is empty.")).toBeInTheDocument();
    expect(callsTo(fetchMock, "/api/predict/batch/validate")).toHaveLength(0);
  });
});
