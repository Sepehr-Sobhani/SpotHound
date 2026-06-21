import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api";
import type { Spot, User } from "../types";
import { Button, Card, Field, inputClass } from "../components/ui";

export default function Admin() {
  const [users, setUsers] = useState<User[]>([]);
  const [spots, setSpots] = useState<Spot[]>([]);
  const [syncMsg, setSyncMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    username: "",
    password: "",
    role: "user",
    telegram_chat_id: "",
  });

  function load() {
    api.listUsers().then(setUsers).catch((e) => setError(e.message));
    api.listSpots().then(setSpots).catch(() => {});
  }
  useEffect(load, []);

  async function createUser(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.createUser({
        username: form.username,
        password: form.password,
        role: form.role,
        telegram_chat_id: form.telegram_chat_id || null,
      });
      setForm({ username: "", password: "", role: "user", telegram_chat_id: "" });
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function sync() {
    const r = await api.syncSpots();
    setSyncMsg(`Synced: ${r.created} created, ${r.updated} updated`);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin</h1>

      <Card>
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Spot catalog</h2>
          <Button variant="ghost" onClick={sync}>
            Sync spots
          </Button>
        </div>
        {syncMsg && <p className="mt-2 text-sm text-emerald-400">{syncMsg}</p>}
        <ul className="mt-3 divide-y divide-slate-700/60 text-sm">
          {spots.map((s) => (
            <li key={s.key} className="flex items-center justify-between py-2">
              <div>
                <p className="font-medium">{s.name}</p>
                <p className="text-xs text-slate-500">{s.key}</p>
              </div>
              <span className="text-xs text-slate-400">
                {s.headless ? "headless" : "headful"}
              </span>
            </li>
          ))}
        </ul>
      </Card>

      <Card>
        <h2 className="mb-4 font-semibold">Users</h2>
        <ul className="mb-5 divide-y divide-slate-700/60 text-sm">
          {users.map((u) => (
            <li key={u.id} className="flex items-center justify-between py-2">
              <span>{u.username}</span>
              <span className="flex items-center gap-3 text-xs text-slate-400">
                <span>{u.role}</span>
                <span>{u.telegram_chat_id ? "telegram ✓" : "no telegram"}</span>
              </span>
            </li>
          ))}
        </ul>

        <form onSubmit={createUser} className="grid gap-3 sm:grid-cols-2">
          <Field label="Username">
            <input
              className={inputClass}
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </Field>
          <Field label="Password">
            <input
              type="password"
              className={inputClass}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </Field>
          <Field label="Role">
            <select
              className={inputClass}
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </Field>
          <Field label="Telegram chat id (optional)">
            <input
              className={inputClass}
              value={form.telegram_chat_id}
              onChange={(e) => setForm({ ...form, telegram_chat_id: e.target.value })}
            />
          </Field>
          <div className="sm:col-span-2">
            <Button type="submit">Create user</Button>
            {error && <span className="ml-3 text-sm text-rose-400">{error}</span>}
          </div>
        </form>
      </Card>
    </div>
  );
}
