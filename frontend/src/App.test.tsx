import { screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { apiError, callsTo, json, mockApi } from "@/test/mockApi";
import { renderApp } from "@/test/render";

describe("App shell and navigation", () => {
  it("renders the overview figures returned by the API", async () => {
    mockApi();
    renderApp("/");
    const figures = await screen.findByRole("region", { name: "Key figures" });
    expect(within(figures).getByText("7,043")).toBeInTheDocument();
    expect(within(figures).getByText("1,869")).toBeInTheDocument();
    expect(within(figures).getByText("26.5%")).toBeInTheDocument();
    // The model-results request failed, so its card explains that instead of breaking the page.
    expect(await screen.findByText("Model results are not available.")).toBeInTheDocument();
  });

  it("navigates between pages from the sidebar", async () => {
    mockApi();
    const { user } = renderApp("/");
    await screen.findByRole("region", { name: "Key figures" });
    const nav = screen.getAllByRole("navigation")[0];
    await user.click(within(nav).getByRole("link", { name: /About the Research/ }));
    expect(await screen.findByRole("heading", { level: 1, name: "About the Research" })).toBeInTheDocument();
    expect(document.title).toBe("About the Research · ChurnIQ");
  });

  it("shows a not-found page for unknown routes", async () => {
    mockApi();
    renderApp("/does-not-exist");
    expect(await screen.findByText("Page not found")).toBeInTheDocument();
  });

  it("shows an error state with retry when the API is unreachable, then recovers", async () => {
    let fail = true;
    mockApi({
      "GET /api/overview": async () => {
        if (fail) throw new TypeError("Failed to fetch");
        const { fixtures } = await import("@/test/mockApi");
        return json(fixtures.overview);
      },
    });
    const { user } = renderApp("/");
    const alert = await screen.findByRole("alert");
    expect(within(alert).getByText("Service unavailable")).toBeInTheDocument();
    fail = false;
    await user.click(within(alert).getByRole("button", { name: /Try again/ }));
    expect(await screen.findByRole("region", { name: "Key figures" })).toBeInTheDocument();
  });

  it("shows the API status in the header", async () => {
    mockApi({ "GET /api/health": () => apiError(503, "down", "down") });
    renderApp("/about");
    expect((await screen.findAllByText("API offline")).length).toBeGreaterThan(0);
  });

  it("reloads the page's data from the top bar and confirms with a toast", async () => {
    const fetchMock = mockApi();
    const { user } = renderApp("/");
    await screen.findByRole("region", { name: "Key figures" });
    expect(callsTo(fetchMock, "/api/overview")).toHaveLength(1);

    await user.click(screen.getByRole("button", { name: "Reload data" }));
    expect(await screen.findByText("Data reloaded")).toBeInTheDocument();
    expect(callsTo(fetchMock, "/api/overview")).toHaveLength(2);
    // Content stays on screen while reloading.
    expect(screen.getByRole("region", { name: "Key figures" })).toBeInTheDocument();
  });
});
