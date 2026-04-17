# RADAR DO GREEN v2.0

## Project Overview
"RADAR DO GREEN | Sinais Roleta Brasileira" — A professional online casino roulette signal web application with dark trading terminal UI, AI-based signal engine, confidence scoring, Telegram bot integration, live radar control, and a full dashboard for Brazilian players.

## Architecture

### Stack
- **Frontend**: React + TypeScript + Vite, Wouter routing, TanStack Query, Shadcn UI
- **Backend**: Node.js + Express.js, session-based auth (express-session)
- **Database**: PostgreSQL via Drizzle ORM (`npm run db:push` to sync schema)
- **Styling**: Tailwind CSS + custom animations, dark-only trading terminal theme

### Key Directories
```
client/src/
  pages/
    login.tsx          # Login page (rebranded RADAR DO GREEN)
    register.tsx       # Register page
    dashboard/
      sinais.tsx       # Live signals feed with confidence bars
      entrada.tsx      # Active signal + countdown + confidence meter
      alertas.tsx      # AI-generated system alerts
      relatorio.tsx    # Performance metrics and win rate report
      suporte.tsx      # VIP support + how it works
      configuracoes.tsx # Telegram config, radar settings, user profile
  components/
    layout/DashboardLayout.tsx  # Main sidebar + header (START/STOP RADAR button)
  hooks/
    use-auth.ts         # Login/register/logout/me
    use-radar.ts        # Health check, radar start/stop, config, telegram test, signal gen
    use-metrics.ts      # Performance metrics from /api/metrics
    use-signals.ts      # Signal list
    use-alerts.ts       # Alerts list
    use-reports.ts      # Report data
    use-user.ts         # Update user profile

server/
  index.ts            # Express app bootstrap
  routes.ts           # All API endpoints + seed data + radar interval
  storage.ts          # DatabaseStorage implementing IStorage
  signal-engine.ts    # AI signal generation, Telegram sender, pattern analysis
  db.ts               # Drizzle DB connection

shared/
  schema.ts           # Drizzle tables + Zod insert schemas + TypeScript types
  routes.ts           # API contract definitions
```

## Design System
- **Font**: Oswald (headings/display), Manrope (body)
- **Primary Color**: Neon Green `hsl(142, 76%, 36%)`
- **Background**: Deep dark `hsl(220, 14%, 4%)`
- **Accent**: Gold `hsl(43, 96%, 50%)`
- **Destructive**: Casino Red `hsl(0, 84%, 58%)`
- **Custom animations**: `radar-pulse`, `live-dot`, `signal-glow-green/red`, `confidence-fill`, `scan`
- **CSS utilities**: `text-glow-green/red/gold`, `box-glow-green/red/gold`, `glass-panel`, `glass-panel-strong`

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | System health + radar status |
| POST | /api/auth/login | Login |
| POST | /api/auth/register | Register |
| GET | /api/auth/me | Current user |
| POST | /api/auth/logout | Logout |
| PUT | /api/users/:id | Update user profile |
| GET | /api/sinais | List signals |
| POST | /api/sinais/generate | AI-generate a signal |
| GET | /api/alertas | List alerts |
| GET | /api/relatorio | Performance report |
| GET | /api/metrics | Dashboard metrics |
| GET | /api/radar/config | Radar configuration |
| PUT | /api/radar/config | Update radar config |
| POST | /api/radar/start | Start auto-signal radar |
| POST | /api/radar/stop | Stop radar |
| POST | /api/radar/telegram/test | Test Telegram connection |

## Signal Engine (server/signal-engine.ts)
- **Pattern analysis**: Tracks last 15 numbers, color frequency, sector clustering (Voisins/Tiers/Orphans)
- **Confidence scoring**: 58–96% based on color imbalance, gap analysis, sector patterns
- **Gale protection**: 2 gales (≥85%), 3 gales (≥70%), 4 gales (<70%)
- **Telegram**: Sends formatted Markdown messages with confidence bar

## Radar Engine
- `POST /api/radar/start` sets radarActive=true and starts a 60s interval
- Every 60s: generates a signal, saves to DB if confidence ≥ threshold, updates report, sends Telegram
- `POST /api/radar/stop` clears interval and sets radarActive=false

## Auth
- Session-based with `express-session`
- Passwords stored in plaintext (no bcrypt) — keep consistent
- Registered dev user: shoponsup@gmail.com / Dukektm.1

## Database Tables
- `users` — id, email, password, name
- `sinais` — id, number, status, confidence, entry, timestamp
- `alertas` — id, message, type, timestamp
- `relatorios` — id, totalSpins, greens, reds, lastNumber, signalsToday, currentStreak, lastSignalResult, updatedAt
- `radar_config` — id, telegramToken, chatId, signalMode, confidenceThreshold, voiceAlerts, radarActive, updatedAt

## Frontend Health Check
- `useHealth()` polls `/api/health` every 5s
- null response → yellow "Modo Simulação" banner in DashboardLayout
- Sidebar shows live dot + "Sistema Online" or yellow "Modo Simulação"
- Radar status synced via health response `.radarActive`

## Seed Data (auto-applied on first boot)
- 7 signals (greens/reds with confidence)
- 2 alerts (sequencia + manipulacao types)
- Report: 247 spins, 163 greens, 84 reds, 18 signals today, streak=5

## Running
```
npm run dev        # Starts Express + Vite on port 5000
npm run db:push    # Sync Drizzle schema to PostgreSQL
```
