# Vercel Frontend Deployment

The Vercel deployment unit is `frontend/`.

Production frontend:

```text
https://startup-sim-khaki.vercel.app
```

Use this URL as the post-push smoke target for frontend changes.

## Build Settings

- Framework: Vite
- Install command: `npm install`
- Build command: `npm run build`
- Output directory: `dist`
- Root directory: `frontend`

These settings are also captured in `frontend/vercel.json`.

## API Mode

The production frontend supports two modes:

- `VITE_API_BASE_URL` set: the frontend calls the configured Startup Sim API.
- `VITE_API_BASE_URL` empty: the frontend enters demo fallback mode so the Vercel page is still playable.

When a real hosted backend is available, set this Vercel environment variable:

```text
VITE_API_BASE_URL=https://your-api-host.example.com
```

To disable demo fallback:

```text
VITE_ENABLE_DEMO_FALLBACK=false
```

## CLI Deploy

From `D:\Startup-sim\frontend`:

```bash
npx vercel --prod
```

If the CLI reports an invalid token, run:

```bash
npx vercel login
```

Then rerun the production deploy command.

## Production Smoke

After a frontend commit is pushed and Vercel finishes deployment, verify:

- The page opens at `https://startup-sim-khaki.vercel.app`.
- The first screen shows the playable command center.
- The page uses "现金流可支撑时间" and does not show "跑道" or "Runway".
- Suggestions stay behind the advice entry until opened.
- A player can submit one turn and see "回合结果".
