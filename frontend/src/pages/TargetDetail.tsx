import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import type { CheckResult, EventItem, Subscriber, Target, User } from "../types";
import {
  Button,
  Card,
  Field,
  Spinner,
  StatusBadge,
  Toggle,
  inputClass,
} from "../components/ui";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function TargetDetail() {
  const { id } = useParams();
  const targetId = Number(id);
  const { user } = useAuth();

  const [target, setTarget] = useState<Target | null>(null);
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [test, setTest] = useState<CheckResult | null>(null);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getTarget(targetId).then(setTarget).catch((e) => setError(e.message));
    api.listSubscribers(targetId).then(setSubscribers).catch(() => {});
    api.listEvents(targetId).then(setEvents).catch(() => {});
    if (user?.role === "admin") api.listUsers().then(setUsers).catch(() => {});
  }, [targetId, user]);

  function set<K extends keyof Target>(key: K, value: Target[K]) {
    setTarget((t) => (t ? { ...t, [key]: value } : t));
  }

  function toggleDay(day: number) {
    const cur = target!.active_days ?? [];
    set(
      "active_days",
      cur.includes(day) ? cur.filter((d) => d !== day) : [...cur, day].sort(),
    );
  }

  async function save() {
    if (!target) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await api.updateTarget(targetId, {
        target_date: target.target_date,
        interval_seconds: target.interval_seconds,
        active_days: target.active_days,
        active_start: target.active_start,
        active_end: target.active_end,
        enabled: target.enabled,
      });
      setTarget(updated);
      setSavedAt(new Date().toLocaleTimeString());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  async function runTest() {
    setTesting(true);
    setTest(null);
    try {
      setTest(await api.testTarget(targetId));
    } catch (e) {
      setTest({ met: false, observed: null, error: (e as Error).message });
    } finally {
      setTesting(false);
    }
  }

  async function addSubscriber(userId: number) {
    await api.subscribeUser(targetId, userId);
    setSubscribers(await api.listSubscribers(targetId));
  }
  async function removeSubscriber(userId: number) {
    await api.unsubscribeUser(targetId, userId);
    setSubscribers(await api.listSubscribers(targetId));
  }

  if (error && !target) return <p className="text-rose-400">{error}</p>;
  if (!target)
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    );

  const subscribedIds = new Set(subscribers.map((s) => s.user_id));
  const available = users.filter((u) => !subscribedIds.has(u.id));

  return (
    <div className="space-y-6">
      <div>
        <Link to="/" className="text-sm text-slate-400 hover:text-white">
          ← Targets
        </Link>
        <div className="mt-2 flex items-center justify-between gap-3">
          <h1 className="text-2xl font-bold">{target.name}</h1>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">{target.enabled ? "On" : "Off"}</span>
            <Toggle on={target.enabled} onClick={() => set("enabled", !target.enabled)} />
          </div>
        </div>
        <div className="mt-2 flex items-center gap-2 text-sm text-slate-400">
          <StatusBadge status={target.last_status} />
          {target.last_checked_at && (
            <span>checked {new Date(target.last_checked_at).toLocaleString()}</span>
          )}
        </div>
      </div>

      <Card>
        <h2 className="mb-4 font-semibold">Schedule</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Date to watch">
            <input
              type="date"
              className={inputClass}
              value={target.target_date ?? ""}
              onChange={(e) => set("target_date", e.target.value || null)}
            />
          </Field>
          <Field label="Check interval (seconds)">
            <input
              type="number"
              min={30}
              className={inputClass}
              value={target.interval_seconds}
              onChange={(e) => set("interval_seconds", Number(e.target.value))}
            />
          </Field>
          <Field label="Active from">
            <input
              type="time"
              className={inputClass}
              value={target.active_start ?? ""}
              onChange={(e) => set("active_start", e.target.value || null)}
            />
          </Field>
          <Field label="Active until">
            <input
              type="time"
              className={inputClass}
              value={target.active_end ?? ""}
              onChange={(e) => set("active_end", e.target.value || null)}
            />
          </Field>
        </div>
        <div className="mt-4">
          <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-400">
            Active days (none = every day)
          </span>
          <div className="flex flex-wrap gap-2">
            {DAYS.map((label, day) => {
              const on = target.active_days?.includes(day) ?? false;
              return (
                <button
                  key={day}
                  onClick={() => toggleDay(day)}
                  className={`rounded-md px-2.5 py-1 text-sm ${
                    on ? "bg-indigo-600 text-white" : "bg-slate-700 text-slate-300"
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
        <div className="mt-5 flex items-center gap-3">
          <Button onClick={save} disabled={saving}>
            {saving ? "Saving…" : "Save changes"}
          </Button>
          {savedAt && <span className="text-sm text-emerald-400">Saved at {savedAt}</span>}
          {error && <span className="text-sm text-rose-400">{error}</span>}
        </div>
      </Card>

      <Card>
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Live test</h2>
          <Button variant="ghost" onClick={runTest} disabled={testing}>
            {testing ? "Running…" : "Run test now"}
          </Button>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          Runs the check immediately (can take ~15s for a real browser).
        </p>
        {testing && (
          <div className="mt-3 flex items-center gap-2 text-sm text-slate-400">
            <Spinner /> checking…
          </div>
        )}
        {test && (
          <div className="mt-3 text-sm">
            {test.error ? (
              <p className="text-rose-400">Error: {test.error}</p>
            ) : (
              <>
                <p className={test.met ? "text-emerald-400" : "text-slate-300"}>
                  {test.met ? "AVAILABLE — would notify" : "Not available"}
                </p>
                <p className="mt-1 text-slate-500">{test.observed}</p>
              </>
            )}
          </div>
        )}
      </Card>

      <Card>
        <h2 className="mb-3 font-semibold">Subscribers</h2>
        <div className="flex flex-wrap gap-2">
          {subscribers.map((s) => (
            <span
              key={s.user_id}
              className="inline-flex items-center gap-2 rounded-full bg-slate-700 px-3 py-1 text-sm"
            >
              {s.username}
              {user?.role === "admin" && (
                <button
                  onClick={() => removeSubscriber(s.user_id)}
                  className="text-slate-400 hover:text-rose-400"
                >
                  ✕
                </button>
              )}
            </span>
          ))}
          {subscribers.length === 0 && (
            <span className="text-sm text-slate-400">No subscribers yet.</span>
          )}
        </div>
        {user?.role === "admin" && available.length > 0 && (
          <div className="mt-4 flex items-center gap-2">
            <select
              className={inputClass + " max-w-xs"}
              defaultValue=""
              onChange={(e) => {
                if (e.target.value) addSubscriber(Number(e.target.value));
                e.target.value = "";
              }}
            >
              <option value="" disabled>
                Add subscriber…
              </option>
              {available.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.username}
                </option>
              ))}
            </select>
          </div>
        )}
      </Card>

      <Card>
        <h2 className="mb-3 font-semibold">Activity</h2>
        {events.length === 0 ? (
          <p className="text-sm text-slate-400">
            No checks yet. Enable the target (or run a test) to see history here.
          </p>
        ) : (
          <ul className="divide-y divide-slate-700/60 text-sm">
            {events.map((ev) => (
              <li key={ev.id} className="flex items-center justify-between gap-3 py-2">
                <div className="flex items-center gap-2">
                  <StatusBadge status={ev.status} />
                  {ev.notified && (
                    <span className="text-xs text-indigo-400">notified</span>
                  )}
                  <span className="truncate text-slate-500" title={ev.observed ?? ""}>
                    {ev.observed}
                  </span>
                </div>
                <span className="shrink-0 text-xs text-slate-500">
                  {new Date(ev.timestamp).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card>
        <h2 className="mb-3 font-semibold">Check logic (read-only)</h2>
        <p className="text-sm text-slate-400">
          Defined in code (<code className="text-slate-300">{target.spot_key}</code>). Edit it by
          updating the spot module.
        </p>
        <dl className="mt-3 space-y-2 text-sm">
          <div>
            <dt className="text-slate-400">URL</dt>
            <dd className="break-all text-slate-200">{target.url}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Steps</dt>
            <dd>
              <pre className="mt-1 overflow-x-auto rounded-md bg-slate-900 p-3 text-xs text-slate-300">
                {JSON.stringify(target.steps, null, 2)}
              </pre>
            </dd>
          </div>
          <div>
            <dt className="text-slate-400">Condition</dt>
            <dd>
              <pre className="mt-1 overflow-x-auto rounded-md bg-slate-900 p-3 text-xs text-slate-300">
                {JSON.stringify(target.condition, null, 2)}
              </pre>
            </dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
