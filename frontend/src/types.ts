export interface Target {
  id: number;
  spot_key: string | null;
  name: string;
  url: string;
  steps: Record<string, unknown>[];
  condition: Record<string, unknown>;
  headless: boolean;
  target_date: string | null;
  interval_seconds: number;
  active_days: number[] | null;
  active_start: string | null;
  active_end: string | null;
  enabled: boolean;
  last_checked_at: string | null;
  last_status: string | null;
  last_observed: string | null;
}

export interface User {
  id: number;
  username: string;
  role: string;
  telegram_chat_id: string | null;
}

export interface CheckResult {
  met: boolean;
  observed: string | null;
  error: string | null;
}

export interface Subscriber {
  user_id: number;
  username: string;
}

export interface Spot {
  key: string;
  name: string;
  url: string;
  headless: boolean;
}
