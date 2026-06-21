import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../auth";
import { Button } from "./ui";
import type { ReactNode } from "react";

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();

  const navLink = (to: string, label: string) => (
    <Link
      to={to}
      className={`text-sm font-medium ${
        pathname === to ? "text-indigo-400" : "text-slate-300 hover:text-white"
      }`}
    >
      {label}
    </Link>
  );

  return (
    <div className="min-h-screen text-slate-100">
      <header className="border-b border-slate-700/60 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-lg font-bold">
              🐕 SpotHound
            </Link>
            <nav className="flex items-center gap-4">
              {navLink("/", "Targets")}
              {navLink("/settings", "Settings")}
              {user?.role === "admin" && navLink("/admin", "Admin")}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-400">{user?.username}</span>
            <Button variant="ghost" onClick={logout}>
              Log out
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
    </div>
  );
}
