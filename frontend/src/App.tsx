import { lazy, Suspense, type ComponentType, type ReactNode } from "react";
import { Route, Routes } from "react-router-dom";

import { InlineLoading } from "@/components/States";
import { AppLayout } from "@/layouts/AppLayout";

// Each page is loaded on demand so the initial bundle stays small.
function page<K extends string>(loader: () => Promise<Record<K, ComponentType>>, name: K) {
  return lazy(() => loader().then((m) => ({ default: m[name] })));
}

const OverviewPage = page(() => import("@/pages/OverviewPage"), "OverviewPage");
const CustomersPage = page(() => import("@/pages/CustomersPage"), "CustomersPage");
const PredictPage = page(() => import("@/pages/PredictPage"), "PredictPage");
const BatchPage = page(() => import("@/pages/BatchPage"), "BatchPage");
const PerformancePage = page(() => import("@/pages/PerformancePage"), "PerformancePage");
const InsightsPage = page(() => import("@/pages/InsightsPage"), "InsightsPage");
const AboutPage = page(() => import("@/pages/AboutPage"), "AboutPage");
const NotFoundPage = page(() => import("@/pages/NotFoundPage"), "NotFoundPage");

const fallback = (
  <div className="py-10">
    <InlineLoading label="Loading page…" />
  </div>
);

export function App() {
  const wrap = (el: ReactNode) => <Suspense fallback={fallback}>{el}</Suspense>;
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={wrap(<OverviewPage />)} />
        <Route path="customers" element={wrap(<CustomersPage />)} />
        <Route path="predict" element={wrap(<PredictPage />)} />
        <Route path="batch" element={wrap(<BatchPage />)} />
        <Route path="performance" element={wrap(<PerformancePage />)} />
        <Route path="insights" element={wrap(<InsightsPage />)} />
        <Route path="about" element={wrap(<AboutPage />)} />
        <Route path="*" element={wrap(<NotFoundPage />)} />
      </Route>
    </Routes>
  );
}
