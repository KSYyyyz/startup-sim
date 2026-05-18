# Vercel Frontend Deployment

The Vercel deployment unit is `frontend/`.

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
