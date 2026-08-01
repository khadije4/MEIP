# Deploying MEIP on Render

MEIP deploys as two Render services from the repository root:

- `meip-api`: Python/FastAPI web service;
- `meip-web`: Vite static site with an SPA rewrite.

The root [`render.yaml`](../render.yaml) is the deployment source of truth.
This hackathon configuration intentionally keeps SQLite. The database is built
from the two committed ANSADE/CN workbooks during every backend build.

## 1. Before pushing

Confirm these files are committed to the Git repository:

```text
data/raw/comptes_nationaux_4.9.1.xlsx
data/raw/comptes_nationaux_4.9.2.xlsx
```

They are required by the Render build command. From the repository root, run:

```powershell
python scripts/import_national_accounts.py
cd apps\api
pytest -q
cd ..\web
npm test
npm run lint
npm run build
```

## 2. Create the Render Blueprint

1. Push the repository to GitHub, GitLab, or Bitbucket.
2. In Render, select **New → Blueprint**.
3. Connect the repository and select the branch to deploy.
4. Render reads `render.yaml` and proposes `meip-api` and `meip-web`.
5. Enter placeholder values when prompted, then create the services.

The backend build performs:

```bash
pip install -r apps/api/requirements.txt && python scripts/import_national_accounts.py
```

The backend starts with Render's assigned port:

```bash
cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The frontend build performs:

```bash
cd apps/web && npm ci && npm run build
```

and publishes `apps/web/dist`. Requests such as `/stress` are rewritten to
`/index.html` so React Router can resolve them.

## 3. Connect the services

After Render assigns both public URLs, configure:

### Static site: `meip-web`

```text
VITE_API_BASE_URL=https://YOUR-BACKEND-SERVICE.onrender.com
```

Do not add a trailing slash. Vite embeds this value at build time, so save it
and trigger a new frontend deployment.

### Backend: `meip-api`

```text
FRONTEND_URL=https://YOUR-FRONTEND-SITE.onrender.com
```

For multiple allowed browser origins, provide a comma-separated value:

```text
FRONTEND_URL=https://meip.onrender.com,https://custom.example.org
```

Do not include URL paths. Saving this value restarts the backend.

## 4. Verify deployment

Open these URLs:

```text
https://YOUR-BACKEND-SERVICE.onrender.com/api/health
https://YOUR-BACKEND-SERVICE.onrender.com/docs
https://YOUR-FRONTEND-SITE.onrender.com/
https://YOUR-FRONTEND-SITE.onrender.com/stress
```

In the browser developer tools, confirm API calls use the HTTPS backend URL
and do not point to `127.0.0.1`.

Generate a PDF from the Reports page. PDF and CSV bytes are generated in
memory and returned directly in the HTTP response; the service does not need a
persistent report directory.

## 5. SQLite behavior

This deployment deliberately does not migrate to PostgreSQL. The application
is read-mostly and rebuilds the normalized SQLite database from the committed
workbooks during each Render build. Runtime filesystem changes are ephemeral
and may disappear after a restart or redeploy. Do not use this configuration
for user-authored persistent data or multiple writing instances.

Use one backend instance. A future production phase can move `DATABASE_URL` to
PostgreSQL without changing the analytical functions.

## Troubleshooting

- **CORS error:** verify `FRONTEND_URL` exactly matches the public static-site
  origin, including `https://` and excluding a trailing slash/path.
- **Frontend calls localhost:** set `VITE_API_BASE_URL` and redeploy the static
  site; Vite environment variables are resolved at build time.
- **Importer cannot find workbooks:** confirm both `.xlsx` files above are
  committed and present in the deployed revision.
- **Deep route returns 404:** confirm the Blueprint includes the `/*` →
  `/index.html` rewrite.
- **First request is slow:** free Render web services may cold-start after an
  idle period.
