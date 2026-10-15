import { useCallback, useEffect, useRef, useState } from "react";

import { useRefreshNonce } from "@/hooks/useRefresh";
import { ApiError } from "@/services/api";

export interface AsyncState<T> {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
  reload: () => void;
}

/** Run an async loader on mount, when deps change, and on a global refresh; ignores stale responses. */
export function useApi<T>(loader: () => Promise<T>, deps: unknown[] = []): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);
  const [nonce, setNonce] = useState(0);
  const requestId = useRef(0);
  const refreshNonce = useRefreshNonce();

  useEffect(() => {
    const id = ++requestId.current;
    setLoading(true);
    setError(null);
    loader()
      .then((d) => {
        if (id === requestId.current) setData(d);
      })
      .catch((e: unknown) => {
        if (id !== requestId.current) return;
        setError(e instanceof ApiError ? e : new ApiError(0, "unknown", "Something went wrong."));
      })
      .finally(() => {
        if (id === requestId.current) setLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce, refreshNonce]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);
  return { data, error, loading, reload };
}
