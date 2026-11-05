# Moving the wiki to Cloudflare Pages (5 Nov 2026)

**Status: decided, built locally, not deployed.** The user chose Cloudflare Pages and a redesigned wiki. Everything in this branch runs on a laptop (wrangler / Miniflare). No Cloudflare account exists yet, nothing is pushed, no DNS has changed.

## What this gives you

- Same static wiki, same URLs, same generators. `scripts/build_site.mjs` copies the repo as it is into `dist/`.
- `/api/roadmap`: the public roadmap, read from D1, cached at the edge, with a static `roadmap.json` fallback.
- `/admin/roadmap`: an editor (add, edit, drag to reorder, change status, delete, restore a previous version), behind Cloudflare Access.
- Room for later features (Discord login, forms into the Discord forums) on the same project. Not built.

## Cost and limits (checked 5 Nov 2026)

Free plan figures, from Cloudflare's docs and pricing pages (the Pages and D1 limits pages, plus the Zero Trust plan page; some figures were confirmed via third-party mirrors, so glance at the official page before you rely on a number):

| Item | Limit on the free plan | This site |
|---|---|---|
| Pages static requests and bandwidth | unlimited, no egress fee | fine |
| Pages files per site | 20,000 | about 4,100 |
| Pages max file size | 25 MiB | largest is `skill_trees.js`, 16 MB |
| Pages builds | 500 per month, counted across the account | we deploy from GitHub Actions, direct upload |
| Pages Functions requests | 100,000 per day, shared with Workers (10 ms CPU each) | roadmap reads are edge-cached, so a few hundred a day |
| D1 | 5 GB per account, 500 MB per database, 5 M rows read and 100 k rows written per day | a few KB |
| Access (Zero Trust) | free for up to 50 users, 24 h log retention | 1 user |
| Domain | you already own 190-expanded.com | $0 |

**Total: $0 per month.** Two changes since the first draft of this plan:
- Cloudflare enforces the free D1 daily limits since 1 Sep 2026 (queries fail past the cap until 00:00 UTC). The roadmap is far below them, and the static fallback covers an outage.
- The Zero Trust free plan may ask for a payment method at sign-up even though it costs nothing.

The paid tier is Workers Paid at $5/month. You would only need it if daily requests ever pass 100,000.

The old 1 GB GitHub Pages worry goes away: Pages has no total-size cap, only the per-file and file-count limits above. Phase 1 in REVIEW.md (thumbnails, split data) is still worth doing for visitors' sake.

## What is in the repo

```
wrangler.toml               Pages project + D1 binding (placeholder id) + non-secret vars
functions/                  Pages Functions, TypeScript
  api/roadmap.ts              GET public roadmap (edge cache, static fallback)
  api/admin/_middleware.ts    Access JWT check for every /api/admin/* call
  api/admin/roadmap/*         list/create, update/delete, reorder, history, restore
  admin/_middleware.ts        Access JWT check for every /admin/* page + CSP, no-store, noindex
  _lib/                       access.ts (JWT), validate.ts, roadmap_db.ts, handlers.ts, http.ts
migrations/0001, 0002   D1 schema: roadmap_items (with progress + wiki link), roadmap_history
db/roadmap_seed.json        DRAFT seed (29 items), also builds db/seed_roadmap.sql and total_war/data/roadmap.json
admin/roadmap.html|js, admin.css    the editor
total_war/roadmap.html + scripts/roadmap.js + styles/roadmap.css    the public page
_routes.json _headers _redirects    Pages routing (/roadmap -> /total_war/roadmap.html)
.github/workflows/deploy.yml        tests -> D1 migrate -> export fallback -> build -> deploy (off until enabled)
tests/                      30 tests: validation, JWT rejection, handlers on a real SQLite
```

## Run it locally (no account, no network)

```
npm install
copy .dev.vars.example .dev.vars        # DEV_BYPASS_ACCESS=1: editor works on localhost only
npm run db:migrate:local
npm run db:seed:local
npm run build:data                      # WebP thumbnails + split data files (needs Python + Pillow)
npm run dev                             # http://localhost:8788
npm test
```

The dev bypass is honoured only when the request host is `localhost`, `127.0.0.1` or `[::1]`, and only when the variable is set. `.dev.vars` is git-ignored. Production has no such variable, and a test proves the flag does nothing on a real host.

## Security model

1. **Cloudflare Access** (edge) puts a login in front of `/admin/*` and `/api/admin/*`. Policy: your email only.
2. **The Function checks the Access token too** (`Cf-Access-Jwt-Assertion`): RS256 signature against the team's published keys, issuer, audience (the Access app's AUD tag), expiry, and an optional email allow-list. Missing, forged, expired or wrong-audience tokens get a 403. If the team domain or AUD is not configured, the endpoints refuse everything (fail closed). So a mistake in the Access policy cannot expose the editor. There are no custom passwords and no sessions of our own.
3. **Request checks on every write:** JSON content type only, `Origin` and `Sec-Fetch-Site` must be this site, body capped at 64 KB. A cross-site form or fetch cannot get through.
4. **Input validation:** title 1 to 80 characters, description up to 280, status and category from fixed lists, date shaped like 2026-11-05, ids positive integers. Every query is parameterised.
5. **Output:** both pages write server text with `textContent` only. The admin pages send a strict CSP (`script-src 'self'`, no inline scripts or styles).
6. **No secrets in the repo.** The Access team domain and AUD tag are identifiers, not secrets. The only secrets are the two GitHub Actions secrets below.

## Steps for you

Do these in order. Each one is safe to stop after.

1. **Cloudflare account.** Sign up (free) at dash.cloudflare.com. Turn on two-factor sign-in.
2. **Log in from the repo (once).** In the repo folder run `npx wrangler login`. A browser opens; approve it.
3. **Create the Pages project** (direct upload, because GitHub Actions deploys it):
   `npx wrangler pages project create 190-expanded --production-branch main`
   The site will be live at `https://190-expanded.pages.dev`.
4. **Create the database:** `npx wrangler d1 create 190-expanded`. Copy the `database_id` it prints into `wrangler.toml` (`database_id = "..."`) and commit that change. An id is not a secret.
   Then load the schema and the draft roadmap:
   `npx wrangler d1 migrations apply DB --remote`   (applies every file in migrations/)
   `npx wrangler d1 execute DB --remote --file db/seed_roadmap.sql`
5. **Set up Cloudflare Access** (Zero Trust dashboard):
   1. Settings, Authentication: make sure **One-time PIN** is enabled as a login method (or add Google / GitHub).
   2. Access, Applications, **Add an application**, **Self-hosted**. Name it "190E admin". Session duration 24 hours.
   3. Public hostnames (destinations), all four: `190-expanded.com` path `admin/*`, `190-expanded.com` path `api/admin/*`, and the same two paths on `190-expanded.pages.dev`.
   4. Policy: **Allow**, Include **Emails**, your email address only. Nothing else.
   5. Save. Copy the **Application Audience (AUD) tag** from the application's overview page. Your **team domain** is shown under Zero Trust, Settings, Custom Pages (it looks like `yourteam.cloudflareaccess.com`).
6. **Give the site those two values.** Either fill them in `wrangler.toml` under `[vars]` (`ACCESS_TEAM_DOMAIN`, `ACCESS_AUD`, and optionally `ACCESS_ALLOWED_EMAILS` with your email) and commit, or set them in the Pages project under Settings, Variables and Secrets. Never set `DEV_BYPASS_ACCESS` in production.
7. **Let GitHub deploy.** In Cloudflare, My Profile, API Tokens, Create Token, Custom: permissions **Account / Cloudflare Pages / Edit** and **Account / D1 / Edit**, scoped to your account. In the GitHub repo, Settings, Secrets and variables, Actions: add secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` (the account id is on the dashboard overview), and a repository **variable** `CLOUDFLARE_DEPLOY_ENABLED` = `true`. Then run the workflow once from the Actions tab (Run workflow).
8. **Test on the preview address, before any DNS change.** Open `https://190-expanded.pages.dev/total_war/roadmap.html` (public page shows the draft items). Open `https://190-expanded.pages.dev/admin/roadmap`: you should get the Cloudflare login, then the editor. Try an edit, a drag, History and Restore. Check that a private window without a login gets the Access screen, not the editor.
9. **Move the domain with no downtime.**
   1. In Cloudflare, **Add a site** `190-expanded.com` (free plan). Cloudflare scans the existing DNS records. Compare them against your registrar's DNS page and add anything missing (especially MX and TXT records if the domain has email). Leave the four GitHub Pages A records (`185.199.108.153`, `.109.153`, `.110.153`, `.111.153`) as they are for now.
   2. A day earlier, lower the TTL on the current records to 300 seconds at the registrar.
   3. At the registrar, change the nameservers to the two Cloudflare gives you. DNS answers stay identical, so the site keeps being served from GitHub Pages with no gap.
   4. When Cloudflare shows the site as Active, open Pages project, **Custom domains**, add `190-expanded.com` (and `www.190-expanded.com`). Cloudflare swaps the GitHub A records for the Pages target. That is the cutover, and it takes effect within a minute or two because the records are proxied.
   5. Check the site and `/admin/roadmap` on the real domain.
   6. **Rollback** if anything is wrong: restore the four A records in Cloudflare DNS. Keep GitHub Pages enabled for about a week as the safety net, then turn it off (Settings, Pages) and delete the repo's `CNAME` file.
10. **Later (not built): Discord login and forms.** Create a Discord application (Developer Portal, OAuth2), add the redirect `https://190-expanded.com/api/auth/callback`, keep the client secret as a Pages secret (`DISCORD_CLIENT_SECRET`), and add one webhook per forum channel as secrets. The code would be a few Functions beside the roadmap ones, with sessions in a signed cookie and users in D1. Ask when you want it.

## Day-to-day after launch

- Edit the roadmap at `/admin/roadmap`. It saves instantly; the public page updates within about two minutes (edge cache), sooner after a save because the editor purges the cached copy.
- Mistake? History, Restore this version. A restore is saved too, so it can be undone.
- Wiki content still comes from the Python generators, committed to `main`. A push to `main` runs the tests and deploys.
- Each deploy refreshes `roadmap.json` from the live database, so the fallback never goes stale.

## Known limits and follow-ups

- The old `total_war/data/roadmap.js` (hand-written stages) is no longer used by any page. Delete it once you are happy with the seed.
- All 29 seed items are marked **Draft**. Some descriptions are thin because the sources were terse (for example Sky City, Chengle road, Yongchang swap). Edit them in the editor.
- The edge cache purge is best effort. If it fails, the public page is at most about two minutes behind.
- History keeps the last 200 saves. No per-user roles: anyone passing Access with an allowed email can edit.
- Not yet done: a WebP thumbnail pipeline and splitting `skill_trees.js` (REVIEW.md, Phase 1).
