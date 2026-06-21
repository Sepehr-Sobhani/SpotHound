import type { ButtonHTMLAttributes, ReactNode } from "react";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "danger";
}) {
  const styles = {
    primary: "bg-indigo-600 hover:bg-indigo-500 text-white",
    ghost: "bg-slate-700 hover:bg-slate-600 text-slate-100",
    danger: "bg-rose-600 hover:bg-rose-500 text-white",
  }[variant];
  return (
    <button
      className={`rounded-md px-3 py-1.5 text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed ${styles} ${className}`}
      {...props}
    />
  );
}

const STATUS_STYLES: Record<string, string> = {
  met: "bg-emerald-500/15 text-emerald-400 ring-emerald-500/30",
  not_met: "bg-slate-500/15 text-slate-300 ring-slate-500/30",
  error: "bg-rose-500/15 text-rose-400 ring-rose-500/30",
  needs_date: "bg-amber-500/15 text-amber-400 ring-amber-500/30",
};

export function StatusBadge({ status }: { status: string | null }) {
  const label = status ?? "never checked";
  const style = STATUS_STYLES[status ?? ""] ?? "bg-slate-500/15 text-slate-400 ring-slate-500/30";
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${style}`}>
      {label === "met" ? "available" : label === "not_met" ? "full" : label}
    </span>
  );
}

export function Toggle({
  on,
  onClick,
  disabled,
}: {
  on: boolean;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
        on ? "bg-indigo-600" : "bg-slate-600"
      } disabled:opacity-50`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
          on ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-slate-700/60 bg-slate-800/50 p-5 ${className}`}>
      {children}
    </div>
  );
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </span>
      {children}
    </label>
  );
}

export const inputClass =
  "w-full rounded-md border border-slate-600 bg-slate-900 px-3 py-1.5 text-sm text-slate-100 outline-none focus:border-indigo-500";

export function Spinner() {
  return (
    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-500 border-t-transparent" />
  );
}
