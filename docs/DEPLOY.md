# Deploying SpotHound

The whole app runs on one small Linux server via Docker: Postgres, the backend
(Playwright + Chromium under xvfb, so bot-protected sites work headless), and
Caddy serving the React app and proxying the API.

## 1. Get a server

Any Ubuntu 22.04+ VM with ~2 GB RAM works. Free option:

- **Oracle Cloud Always Free** — an Ampere (ARM) VM is free forever. Sign up at
  cloud.oracle.com (needs a card for verification, not charged), create an
  "Always Free eligible" VM instance with Ubuntu, and add an ingress rule for
  ports 80 and 443.

(Any other VPS works too — DigitalOcean/Hetzner are ~$5/mo and have no signup
friction.)

## 2. Install Docker on the server

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER     # then log out/in
```

## 3. Get the code and configure

```bash
git clone https://github.com/Sepehr-Sobhani/SpotHound.git
cd SpotHound
cp .env.prod.example .env.prod
nano .env.prod
```

Fill in `.env.prod`:
- `JWT_SECRET` — `openssl rand -base64 48`
- `POSTGRES_PASSWORD` — a strong value (keep it in sync inside `DATABASE_URL`)
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — your login
- `TELEGRAM_BOT_TOKEN` — from @BotFather
- `SITE_ADDRESS` — leave `:80` for HTTP on the server IP, or set a domain (see below)

## 4. Deploy

```bash
./deploy.sh
```

This builds the images (the backend pulls Chromium, so the first build takes a
few minutes), starts everything, and seeds the admin user + spots. Open
`http://<server-ip>/` and log in.

Open the firewall for ports 80/443 (Oracle: also `sudo iptables` / security
list; Ubuntu ufw: `sudo ufw allow 80,443/tcp`).

## 5. HTTPS (recommended)

Point a domain's A record at the server IP, set `SITE_ADDRESS=yourdomain.com` in
`.env.prod`, and re-run `./deploy.sh`. Caddy fetches a Let's Encrypt certificate
automatically. No domain? A free `*.duckdns.org` subdomain works.

## Updating

```bash
git pull
./deploy.sh        # rebuilds and restarts; data in Postgres is preserved
```

## Notes

- Spots are off by default after seeding — enable the ones you want in the UI.
- Telegram: in the app, Settings → message the bot → "Find recent chat ids" →
  Use → Save → Send test.
- Logs: `docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f backend`
