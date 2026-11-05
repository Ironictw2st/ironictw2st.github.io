# STATUS 5 Nov 2026: undecided

The user first said "stay on GitHub Pages" (too much overhead), then asked whether the 1 GB Pages limit makes Cloudflare Pages worth it. The site is currently ~621 MB, i.e. under the limit, and Phase 1 in REVIEW.md (thumbnails, split data) shrinks what is served either way. A **hosting-only move** (same static files, no login/forms) is the low-overhead option: see the summary below. Logins/forms are only possible after moving.

# Migration plan: GitHub Pages → a host with logins + forms (5 Nov 2026)

Goal: keep the static wiki, add (1) Discord login, (2) bug-report / suggestion forms that land in the Discord forum channels, (3) optional per-user favourites. Nothing here has been deployed; no accounts created, no DNS touched.

Plan limits below are from memory of each vendor's public pricing (late 2025/2026). **Re-check the pricing pages before committing**; the figures are for orientation, not a quote.

## Constraints from this site

- 621 MB / ~4,100 files (472 MB images), growing; 27 MB of JS data on the heaviest page.
- Traffic is modest (53K subscribers, a wiki) but bursty after updates.
- Needs: custom domain `190-expanded.com`, Discord OAuth2, a small relational store (users, reports, favourites), server-side secret for the Discord webhook/bot, keep the Python generators + git workflow.
- Owner is a solo modder: ease of setup and zero running cost matter more than scale.

## Comparison

| | **Cloudflare Pages + Workers + D1 (+R2)** | Vercel + Supabase | Netlify + Supabase |
|---|---|---|---|
| Static hosting limits (free) | 20,000 files/site, 25 MiB/file, unlimited bandwidth; 500 builds/mo. 4.1K files fits. | Hobby: 100 GB/mo bandwidth, deployment-size caps (~100 MB class for CLI uploads; large static trees are awkward) | 100 GB/mo bandwidth (credit-based on newer plans); 621 MB deploy is allowed but slow deploys |
| Bandwidth risk | none (no egress charge) | overage → upgrade to Pro ($20/user/mo); Hobby is non-commercial only | overage → paid plan ($19/mo/member class) |
| Large images | put `data/images` in **R2** (10 GB free, $0 egress) or leave in Pages | needs Blob/S3 for the 472 MB | needs Large Media or external S3 |
| API / forms | Workers (100k req/day free); same-origin `/api/*` | Serverless functions (limits per Hobby) | Netlify Functions (125k/mo free) |
| DB | **D1** (SQLite) 5 GB, 5M reads + 100k writes/day free | Supabase Postgres 500 MB free; **free projects pause after a week of inactivity** | same Supabase limits |
| Discord OAuth | hand-rolled in a Worker (~80 lines, standard authorization-code flow) | Supabase Auth has a built-in Discord provider | same |
| Custom domain | free, apex via CNAME flattening if DNS is moved to Cloudflare (or CNAME `www`) | free | free |
| Cost for this site | **$0** (Workers Paid is $5/mo if ever needed) | $0 now, ~$45/mo realistic once past limits | $0 now, ~$19–25/mo once past limits |
| Ease | one vendor, one dashboard, `wrangler` CLI; GitHub integration builds on push | two vendors to wire | two vendors to wire |
| Main downside | Discord OAuth is DIY; D1 is SQLite (fine here) | pause-on-idle DB; non-commercial Hobby clause | same as Vercel for DB |

## Recommendation: Cloudflare Pages + Workers + D1 (+ R2 for images)

**Cost: $0/month** at this scale (domain is already owned). No egress fees is the deciding factor given 472 MB of images and a heavy character page. Optional later: Workers Paid $5/mo if daily request limits are ever hit.

### Architecture

```
 browser ──► Cloudflare Pages  (static wiki: index.html, total_war/**, tools/**, data JS)
        └──► /api/*  (Pages Functions or one Worker on the same domain)
                ├─ GET  /api/auth/login      → redirect to Discord OAuth2 (scope: identify), state cookie
                ├─ GET  /api/auth/callback   → exchange code, fetch /users/@me, upsert user in D1,
                │                               set signed HttpOnly+Secure+SameSite=Lax session cookie
                ├─ POST /api/auth/logout
                ├─ GET  /api/me
                ├─ POST /api/report          → validate + rate-limit, insert row in D1, post to Discord forum
                ├─ POST /api/suggestion      → same, different forum channel
                └─ GET/PUT /api/favourites   → optional: per-user character/faction favourites
 D1 tables: users(discord_id PK, name, avatar, created), reports(id, user_id, kind, title, body,
            game_version, discord_thread_id, created), favourites(user_id, kind, key)
 R2 (optional): data/images + UI art, served via a custom domain `img.190-expanded.com`
```

Discord side. **Forum posts:** a webhook created on a forum channel can start a thread (`thread_name` in the execute-webhook payload; embed carries the report body, username, game version). Start with a webhook per forum (bug reports, suggestions): no bot hosting, secret lives in a Worker secret. If the bot must read replies back or close threads, the existing bot (bugcat) can poll D1 or be called by a Worker via its token instead; decide later. Show reporter as "Name (Discord)" only after OAuth; anonymous submissions allowed behind Turnstile if wanted.

Guard rails: Cloudflare Turnstile on forms (free), per-user + per-IP rate limit (D1 counter or the Workers rate-limit binding), 4 KB body cap, strip `@everyone/@here` (`allowed_mentions: {parse: []}`), HTML-escape everything rendered back.

### Generator / deploy pipeline

- GitHub repo stays source of truth. Cloudflare Pages connected to `Ironictw2st/ironictw2st.github.io` (or Direct Upload via GitHub Actions + `wrangler pages deploy`): push to `main` = production, other branches (e.g. `redesign`) = preview URL for review.
- The Python generators keep running locally against the mod tree (they read `Z:\Claude\190Expanded\…`, which CI cannot see), then the committed output is deployed. GitHub Action (`.github/workflows/deploy.yml`): checkout → (optional) `python generate_data/audit_site.py` as a gate → `wrangler pages deploy . --project-name=…` and `wrangler d1 migrations apply`.
- Image pipeline to add: a generator step producing 160/480 px WebP thumbnails; originals go to R2 via `rclone`/`wrangler r2 object put` (not in the Pages bundle), which also takes the repo from 621 MB toward ~150 MB.
- Rollback: Pages keeps every deployment; keep GitHub Pages live until cut-over is verified.

### Steps for the user (nothing done yet)

1. Create a free Cloudflare account; add the site (Workers & Pages → Create → Pages → connect GitHub repo, authorise the Cloudflare GitHub app on that one repo).
2. Create D1 database `wiki` and (optional) R2 bucket `wiki-assets`; I supply `schema.sql` + `wrangler.toml`.
3. Discord Developer Portal: New Application → OAuth2 → add redirect `https://190-expanded.com/api/auth/callback` (and the `*.pages.dev` preview URL for testing) → copy Client ID + Secret.
4. Discord: in each forum channel → Integrations → Webhooks → New webhook → copy URL (one for bugs, one for suggestions).
5. Cloudflare Pages project → Settings → Variables and Secrets (as **secrets**, never in the repo): `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `SESSION_SECRET` (32 random bytes), `WEBHOOK_BUGS`, `WEBHOOK_SUGGESTIONS`, `TURNSTILE_SECRET`; public var `TURNSTILE_SITEKEY`.
6. DNS: simplest is to move the `190-expanded.com` nameservers to Cloudflare (free), then Pages → Custom domains → add `190-expanded.com` + `www`. Keep the old CNAME untouched until the preview passes; then switch and remove the GitHub Pages custom domain. TTL low (300 s) during the change.
7. Test on the `*.pages.dev` preview (login, a report landing in a test forum), then flip DNS.

No secret ever goes into the repo; `.dev.vars` (local wrangler secrets) is git-ignored.

### Staging order (suggested)

1. Re-host the static site on Cloudflare Pages unchanged (or with the `redesign` branch) — zero-risk, proves domain + deploy.
2. Move images to R2 + thumbnails.
3. Add `/api/auth/*` + `/api/me` (login button in the nav).
4. Add report/suggestion forms → D1 + Discord webhook.
5. Favourites, then per-character permalinks/OG tags via a Function.

### If Cloudflare is rejected

Fallback: stay on GitHub Pages for the wiki and put only `/api` on a Cloudflare Worker at `api.190-expanded.com` (CORS-allow the wiki origin; cookies on the parent domain). Same Worker code, no migration of the static site, but the 1 GB GitHub Pages ceiling remains a problem for the images.
