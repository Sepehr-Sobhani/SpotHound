import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { Target } from "../types";
import { Card, Spinner, StatusBadge, Toggle } from "../components/ui";

export default function Dashboard() {
  const [targets, setTargets] = useState<Target[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listTargets().then(setTargets).catch((e) => setError(e.message));
  }, []);

  async function toggle(t: Target) {
    const updated = await api.toggleTarget(t.id);
    setTargets((cur) => cur!.map((x) => (x.id === t.id ? updated : x)));
  }

  if (error) return <p className="text-rose-400">{error}</p>;
  if (!targets)
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    );

  return (
    <div>
      <h1 className="mb-1 text-2xl font-bold">Targets</h1>
      <p className="mb-6 text-sm text-slate-400">
        Spots being watched. Toggle a target on to start checking on its schedule.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {targets.map((t) => (
          <Card key={t.id}>
            <div className="flex items-start justify-between gap-3">
              <Link to={`/targets/${t.id}`} className="font-semibold hover:text-indigo-400">
                {t.name}
              </Link>
              <Toggle on={t.enabled} onClick={() => toggle(t)} />
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-slate-400">
              <StatusBadge status={t.last_status} />
              <span>·</span>
              <span>{t.target_date ?? "no date set"}</span>
              <span>·</span>
              <span>every {t.interval_seconds}s</span>
            </div>
            {t.last_observed && (
              <p className="mt-2 truncate text-xs text-slate-500" title={t.last_observed}>
                {t.last_observed}
              </p>
            )}
          </Card>
        ))}
        {targets.length === 0 && (
          <p className="text-slate-400">
            No targets yet. An admin adds spots in code, then syncs them.
          </p>
        )}
      </div>
    </div>
  );
}
