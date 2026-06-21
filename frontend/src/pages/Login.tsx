import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { Button, inputClass } from "../components/ui";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 text-slate-100">
      <form
        onSubmit={submit}
        className="w-full max-w-sm rounded-xl border border-slate-700/60 bg-slate-800/50 p-8"
      >
        <h1 className="mb-1 text-2xl font-bold">🐕 SpotHound</h1>
        <p className="mb-6 text-sm text-slate-400">Sign in to manage your watches.</p>
        <div className="space-y-4">
          <input
            className={inputClass}
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
          <input
            className={inputClass}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? "Signing in…" : "Sign in"}
          </Button>
        </div>
      </form>
    </div>
  );
}
