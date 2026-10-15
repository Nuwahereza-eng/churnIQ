import { ChevronRight, Menu, PanelLeftClose, PanelLeftOpen, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

import { ResearchNotice } from "@/components/ResearchNotice";
import { ToastProvider, useToast } from "@/components/Toaster";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { RefreshContext } from "@/hooks/useRefresh";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";

import { ApiStatus } from "./ApiStatus";
import { Logo } from "./Logo";
import { NAV_ITEMS } from "./nav";
import { SidebarNav } from "./SidebarNav";

const STORAGE_KEY = "churniq.sidebar.collapsed";

function readCollapsed() {
  try {
    return localStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false;
  }
}

export function AppLayout() {
  return (
    <ToastProvider>
      <Shell />
    </ToastProvider>
  );
}

function Shell() {
  const [collapsed, setCollapsed] = useState(readCollapsed);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [nonce, setNonce] = useState(0);
  const [reloading, setReloading] = useState(false);
  const notify = useToast();
  const location = useLocation();
  const current = NAV_ITEMS.find((n) => (n.to === "/" ? location.pathname === "/" : location.pathname.startsWith(n.to)));

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, collapsed ? "1" : "0");
    } catch {
      /* storage unavailable */
    }
  }, [collapsed]);

  useEffect(() => {
    document.title = current ? `${current.label} · ChurnIQ` : "ChurnIQ";
    window.scrollTo?.(0, 0);
  }, [current]);

  // Re-run every data request on the current page, then confirm the API answered.
  const reload = useCallback(async () => {
    setReloading(true);
    setNonce((n) => n + 1);
    try {
      await api.health();
      notify({ variant: "success", title: "Data reloaded", description: "Figures on this page were fetched again from the API." });
    } catch {
      notify({ variant: "error", title: "Cannot reach the API", description: "Check that the backend is running, then try again." });
    } finally {
      setReloading(false);
    }
  }, [notify]);

  return (
    <RefreshContext.Provider value={nonce}>
      <div className="min-h-screen">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-card focus:px-3 focus:py-2 focus:shadow-md"
        >
          Skip to content
        </a>

        {/* Desktop sidebar */}
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-30 hidden flex-col border-r border-border bg-card transition-[width] duration-200 lg:flex",
            collapsed ? "w-[72px]" : "w-64",
          )}
        >
          <div className={cn("flex h-16 items-center", collapsed ? "justify-center" : "px-5")}>
            <Link to="/" aria-label="ChurnIQ overview" className="rounded-lg">
              <Logo collapsed={collapsed} />
            </Link>
          </div>
          <div className={cn("flex-1 overflow-y-auto py-3", collapsed ? "px-3" : "px-3")}>
            <SidebarNav collapsed={collapsed} />
          </div>
          {!collapsed && (
            <div className="m-3 rounded-xl bg-subtle p-3">
              <ResearchNotice compact />
            </div>
          )}
        </aside>

        <div className={cn("flex min-h-screen flex-col transition-[padding] duration-200", collapsed ? "lg:pl-[72px]" : "lg:pl-64")}>
          {/* Top bar */}
          <header className="sticky top-0 z-20 flex h-16 items-center gap-2 border-b border-border bg-card/90 px-4 backdrop-blur-md sm:gap-3 sm:px-6">
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Open navigation">
                  <Menu />
                </Button>
              </SheetTrigger>
              <SheetContent title="Navigation">
                <div className="flex h-16 items-center px-5">
                  <Logo />
                </div>
                <div className="flex-1 overflow-y-auto px-3 py-3">
                  <SidebarNav onNavigate={() => setMobileOpen(false)} />
                </div>
                <div className="m-3 rounded-xl bg-subtle p-3">
                  <ResearchNotice compact />
                </div>
              </SheetContent>
            </Sheet>
            <Button
              variant="ghost"
              size="icon"
              className="hidden lg:inline-flex"
              onClick={() => setCollapsed((c) => !c)}
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              aria-pressed={collapsed}
            >
              {collapsed ? <PanelLeftOpen /> : <PanelLeftClose />}
            </Button>
            <div className="lg:hidden">
              <Logo collapsed />
            </div>

            <nav aria-label="Breadcrumb" className="min-w-0">
              <ol className="flex min-w-0 items-center gap-1.5 text-sm">
                <li className="hidden text-muted-foreground sm:block">ChurnIQ</li>
                <li aria-hidden className="hidden text-muted-foreground sm:block">
                  <ChevronRight className="size-4" />
                </li>
                <li className="truncate font-medium text-foreground" aria-current="page">
                  {current?.label ?? "Page not found"}
                </li>
              </ol>
            </nav>

            <div className="ml-auto flex items-center gap-1.5 sm:gap-2">
              <ApiStatus />
              <Button
                variant="ghost"
                size="icon"
                onClick={reload}
                disabled={reloading}
                aria-label="Reload data"
                title="Reload data from the API"
              >
                <RefreshCw className={cn(reloading && "animate-spin")} />
              </Button>
            </div>
          </header>

          <main id="main" className="mx-auto w-full max-w-[1440px] flex-1 px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
            <Outlet />
          </main>
          <footer className="border-t border-border bg-card px-4 py-4 sm:px-6 lg:px-8">
            <ResearchNotice />
          </footer>
        </div>
      </div>
    </RefreshContext.Provider>
  );
}
