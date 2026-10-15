import { describe, expect, it, vi } from "vitest";

import { apiError, mockApi } from "@/test/mockApi";

import { api, ApiError } from "./api";

describe("api client", () => {
  it("converts the backend error envelope into an ApiError", async () => {
    mockApi({ "GET /api/overview": () => apiError(503, "dataset_unavailable", "Dataset missing.", ["Run download_data.py"]) });
    const err = await api.overview().catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err).toMatchObject({ status: 503, code: "dataset_unavailable", message: "Dataset missing.", details: ["Run download_data.py"] });
  });

  it("reports a network failure as status 0", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    await expect(api.health()).rejects.toMatchObject({ status: 0, code: "network_error" });
  });

  it("serialises customer filters as query parameters, skipping empty ones", async () => {
    const fetchMock = mockApi({ "GET /api/customers": () => new Response("{}") });
    await api.customers({ page: 2, search: "", contract: ["One year", "Two year"] } as never);
    const url = new URL(String(fetchMock.mock.calls[0][0]), "http://localhost");
    expect(url.searchParams.get("page")).toBe("2");
    expect(url.searchParams.has("search")).toBe(false);
    expect(url.searchParams.getAll("contract")).toEqual(["One year", "Two year"]);
  });
});
