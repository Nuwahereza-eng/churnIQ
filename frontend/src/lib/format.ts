const intFormat = new Intl.NumberFormat("en-US");

export const formatInt = (n: number) => intFormat.format(n);

export const formatPct = (x: number, digits = 1) => `${(x * 100).toFixed(digits)}%`;

export const formatNum = (x: number, digits = 3) => x.toFixed(digits);

export const formatMoney = (x: number) => x.toFixed(2);

export function formatDate(iso: string) {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}
