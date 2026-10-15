import {
  BarChart3,
  BookOpen,
  FileSpreadsheet,
  Gauge,
  LayoutDashboard,
  Lightbulb,
  Users,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

export interface NavGroup {
  label: string | null;
  items: NavItem[];
}

export const NAV_GROUPS: NavGroup[] = [
  {
    label: "Explore",
    items: [
      { to: "/", label: "Overview", icon: LayoutDashboard },
      { to: "/customers", label: "Customer Explorer", icon: Users },
    ],
  },
  {
    label: "Predict",
    items: [
      { to: "/predict", label: "Predict Churn", icon: Gauge },
      { to: "/batch", label: "Batch Predictions", icon: FileSpreadsheet },
    ],
  },
  {
    label: "Evaluate",
    items: [
      { to: "/performance", label: "Model Performance", icon: BarChart3 },
      { to: "/insights", label: "Insights", icon: Lightbulb },
    ],
  },
  { label: null, items: [{ to: "/about", label: "About the Research", icon: BookOpen }] },
];

export const NAV_ITEMS: NavItem[] = NAV_GROUPS.flatMap((g) => g.items);
