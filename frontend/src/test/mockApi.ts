import { vi } from "vitest";

import batchPredict from "./fixtures/batch_predict.json";
import batchValidate from "./fixtures/batch_validate.json";
import health from "./fixtures/health.json";
import overview from "./fixtures/overview.json";
import predict from "./fixtures/predict.json";
import schema from "./fixtures/schema.json";

// Fixtures are responses captured from the real API, so tests use genuine values.
export const fixtures = { batchPredict, batchValidate, health, overview, predict, schema };

export type Handler = (init?: RequestInit) => Response | Promise<Response>;

export const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

export const apiError = (status: number, code: string, message: string, details: string[] = []) =>
  json({ error: { code, message, details } }, status);

const defaults: Record<string, Handler> = {
  "GET /api/health": () => json(health),
  "GET /api/schema": () => json(schema),
  "GET /api/overview": () => json(overview),
  "GET /api/model/metrics": () => apiError(503, "results_unavailable", "Model results are not available."),
  "POST /api/predict": () => json(predict),
  "POST /api/predict/batch/validate": () => json(batchValidate),
  "POST /api/predict/batch": () => json(batchPredict),
};

/** Replace fetch with a router over `METHOD /path` keys; returns the mock for call assertions. */
export function mockApi(overrides: Record<string, Handler> = {}) {
  const routes = { ...defaults, ...overrides };
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    const key = `${init?.method ?? "GET"} ${url.pathname}`;
    const handler = routes[key];
    if (!handler) throw new Error(`Unmocked request: ${key}`);
    return handler(init);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

export const callsTo = (fetchMock: ReturnType<typeof mockApi>, path: string) =>
  fetchMock.mock.calls.filter(([input]) => new URL(String(input), "http://localhost").pathname === path);
