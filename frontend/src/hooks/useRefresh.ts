import { createContext, useContext } from "react";

/**
 * Incremented by the top bar's reload control. useApi includes it in its
 * dependencies, so every visible data request runs again without remounting
 * pages (form input and filters are kept).
 */
export const RefreshContext = createContext(0);

export const useRefreshNonce = () => useContext(RefreshContext);
