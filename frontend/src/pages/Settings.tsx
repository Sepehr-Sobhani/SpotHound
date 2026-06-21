import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth";
import type { ChatUpdate, TelegramStatus } from "../types";
import { Button, Card, Field, inputClass } from "../components/ui";

export default function Settings() {
  const { user, refresh } = useAuth();
  const [status, setStatus] = useState<TelegramStatus | null>(null);
  const [chatId, setChatId] = useState(user?.telegram_chat_id ?? "");
  const [updates, setUpdates] = useState<ChatUpdate[] | null>(null);
  const [msg, setMsg] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  useEffect(() => {
    api.telegramStatus().then(setStatus).catch(() => {});
  }, []);

  async function save() {
    setMsg(null);
    try {
      await api.updateMe(chatId || null);
      await refresh();
      setMsg({ kind: "ok", text: "Saved." });
    } catch (e) {
      setMsg({ kind: "err", text: (e as Error).message });
    }
  }

  async function sendTest() {
    setMsg(null);
    try {
      await api.testMyTelegram();
      setMsg({ kind: "ok", text: "Test sent — check Telegram." });
    } catch (e) {
      setMsg({ kind: "err", text: (e as Error).message });
    }
  }

  async function discover() {
    setUpdates(await api.telegramUpdates());
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Notification settings</h1>

      <Card>
        <h2 className="mb-2 font-semibold">Telegram</h2>
        {status === null ? (
          <p className="text-sm text-slate-400">Checking bot status…</p>
        ) : status.configured ? (
          <p className="text-sm text-slate-300">
            Bot connected:{" "}
            <span className="font-medium text-indigo-400">@{status.username}</span>. Open it in
            Telegram and send any message first, so it can reach you.
          </p>
        ) : (
          <p className="text-sm text-amber-400">
            No bot token configured. Set <code>TELEGRAM_BOT_TOKEN</code> in the backend{" "}
            <code>.env</code> (from @BotFather) and restart the API.
          </p>
        )}

        <div className="mt-4 max-w-md space-y-3">
          <Field label="Your Telegram chat id">
            <input
              className={inputClass}
              value={chatId}
              onChange={(e) => setChatId(e.target.value)}
              placeholder="e.g. 16044404033"
            />
          </Field>
          <div className="flex items-center gap-3">
            <Button onClick={save}>Save</Button>
            <Button variant="ghost" onClick={sendTest}>
              Send test
            </Button>
            {msg && (
              <span className={msg.kind === "ok" ? "text-sm text-emerald-400" : "text-sm text-rose-400"}>
                {msg.text}
              </span>
            )}
          </div>
        </div>

        {user?.role === "admin" && status?.configured && (
          <div className="mt-6 border-t border-slate-700/60 pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-400">
                Don't know your chat id? Message the bot, then look it up here.
              </p>
              <Button variant="ghost" onClick={discover}>
                Find recent chat ids
              </Button>
            </div>
            {updates && (
              <ul className="mt-3 divide-y divide-slate-700/60 text-sm">
                {updates.map((u) => (
                  <li key={u.chat_id} className="flex items-center justify-between py-2">
                    <span>
                      <span className="font-medium">{u.name}</span>{" "}
                      <span className="text-slate-500">({u.chat_id})</span>
                    </span>
                    <Button variant="ghost" onClick={() => setChatId(u.chat_id)}>
                      Use
                    </Button>
                  </li>
                ))}
                {updates.length === 0 && (
                  <li className="py-2 text-slate-400">
                    No recent messages. Send the bot a message, then try again.
                  </li>
                )}
              </ul>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
