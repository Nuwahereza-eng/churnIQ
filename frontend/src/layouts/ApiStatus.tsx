import { useEffect, useState } from "react";

import { useRefreshNonce } from "@/hooks/useRefresh";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";
import type { Health } from "@/types/api";

type Status = "checking" | "ok" | "degraded" | "offline";

/** Compact dataset/model status chip (polls /api/health and re-checks on reload). */
export function ApiStatus() {
  const [status, setStatus] = useState<Status>("checking");
  const [health, setHealth] = useState<Health | null>(null);
  const nonce = useRefreshNonce();

  useEffect(() => {
    let alive = true;
    const check = () =>
      api
        .health()
        .then((h) => {
          if (!alive) return;
          setHealth(h);
          setStatus(h.status);
        })
        .catch(() => alive && setStatus("offline"));
    check();
    const t = setInterval(check, 30_000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, [nonce]);

  const missing = health
    ? [!health.dataset_available && "dataset", !health.model_available && "model", !health.results_available && "results"].filter(Boolean)
    : [];
  const label = {
    checking: "Checking API…",
    ok: "Dataset and model ready",
    degraded: `Missing: ${missing.join(", ")}`,
    offline: "API offline",
  }[status];
  const detail = status === "ok" && health?.model_name ? health.model_name : null;
  const style = {
    checking: "bg-muted text-muted-foreground",
    ok: "bg-success-soft text-success",
    degraded: "bg-warning-soft text-warning-foreground",
    offline: "bg-danger-soft text-danger",
  }[status];
  const dot = { checking: "bg-[#9aa0a6]", ok: "bg-success", degraded: "bg-warning", offline: "bg-danger" }[status];

  return (
    <div
      role="status"
      aria-live="polite"
      title={detail ? `${label} · ${detail}` : label}
      className={cn("flex h-8 items-center gap-2 rounded-lg px-2.5 text-xs font-medium", style)}
    >
      <span aria-hidden className={cn("size-2 shrink-0 rounded-full", dot, status === "checking" && "animate-pulse")} />
      <span className="hidden sm:inline">{label}</span>
      {detail && <span className="hidden font-normal text-[#3c4043] xl:inline">· {detail}</span>}
      <span className="sr-only sm:hidden">{label}</span>
    </div>
  );
}
