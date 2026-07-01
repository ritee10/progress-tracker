# Progress Tracker — Production Deployment Guide

This guide covers the deployment of the Progress Tracker application using **Render** (Backend), **Vercel** (Frontend), and **Supabase** (PostgreSQL & Storage).

---

## 1. Supabase Database & Storage Setup

### Database Creation
1. Create a new project in [Supabase](https://supabase.com).
2. Go to **Settings > Database** and enable **Connection Pooling**.
3. Use the **Transaction Pooler URL** (port `6543`) for your backend configuration.

### Storage Configuration
1. Go to **Storage > Create a new bucket**.
2. Name the bucket `uploads`.
3. Set the bucket to **Public**.

---

## 2. Backend Deployment (Render)

The backend is configured to use Render via the `render.yaml` Blueprint.

### Steps
1. Push your repository to GitHub.
2. Log into [Render](https://render.com) and click **New > Blueprint**.
3. Connect your repository. Render will automatically detect the `render.yaml` file.
4. Set the following Environment Variables in the Render Dashboard:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Supabase async pooler string (e.g. `postgresql+asyncpg://...:6543/postgres`) |
| `DATABASE_URL_SYNC` | Supabase sync pooler string (e.g. `postgresql+psycopg2://...:6543/postgres`) |
| `SUPABASE_URL` | Supabase Project URL |
| `SUPABASE_KEY` | Supabase Project API Key (anon/service-role) |
| `CORS_ORIGINS` | `["https://your-frontend.vercel.app"]` |

Render will automatically run `alembic upgrade head` on deployment.

---

## 3. Frontend Deployment (Vercel)

The frontend is deployed to Vercel, optimized as a Single Page Application (SPA).

### Steps
1. Log into [Vercel](https://vercel.com) and click **Add New Project**.
2. Import your GitHub repository.
3. Configure the Project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
4. Add the Environment Variable:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://progress-tracker-api.onrender.com/api/v1`)
5. Deploy. The `vercel.json` file handles all SPA routing.

---

## 4. GitHub Actions CI/CD

The `.github/workflows` folder contains two workflows:
- **`backend.yml`**: Runs `pytest` on push to the `main` branch. Deploys to Render via deploy hook if successful.
  - Requires GitHub Secrets: `RENDER_SERVICE_ID`, `RENDER_DEPLOY_HOOK_KEY`.
- **`frontend.yml`**: Runs `npm run build` and `npm run lint` on push to the `main` branch to catch errors. Actual deployment is handled automatically by the Vercel GitHub integration.

---

## 5. Security & Performance Features

### Security Hardening Included
- **JWT Authentication**: Configured with expiring access and refresh tokens.
- **CORS Allowlist**: Set strictly via the `CORS_ORIGINS` env variable.
- **Security Headers Middleware**: Implemented `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, and `Strict-Transport-Security`.
- **Rate Limiting**: Configured to 100 requests/minute.
- **Parameterized SQL**: Enforced natively via SQLAlchemy core.

### Performance Optimizations Included
- **Vite Chunk Splitting**: Vendor dependencies, UI components, and data fetching libraries are split into separate chunks for optimal caching.
- **Database Pooling**: Configured SQLAlchemy with `pool_size=20` and `max_overflow=10`, complemented by Supabase's transaction pooler.
- **SPA Routing**: Vercel `vercel.json` routing bypasses backend HTML serving, fully decoupling the UI.

---

## 6. Production Readiness Checklist

- [ ] Database migrated using Alembic
- [ ] Backend deployed and passing `/health` check
- [ ] Vercel frontend deployed and using the correct `VITE_API_URL`
- [ ] CORS explicitly defined in Render matching the Vercel domain
- [ ] All environment variables set (including rotating `SECRET_KEY` and `JWT_SECRET_KEY`)
- [ ] PDF upload functionality tested pointing to Supabase `uploads` bucket
