# RoparCat

RoparCat is a fork of Tabbycat for IIT Ropar debate tournaments.

## Rules

- The license is AGPL-3.0. Never remove copyright notices or Tabbycat credits.
- We run everything through docker compose. Use `docker compose exec web python tabbycat/manage.py ...` for management commands (the container's working directory is `/tcd`; `manage.py` lives in `tabbycat/`).
- Run the relevant tests after every change to draw, results, or standings code:
  `docker compose exec web python tabbycat/manage.py test draw results standings --exclude-tag=selenium --noinput`
- Never commit or push without showing me the diff first.

## Docker gotchas

- `docker compose up` refuses to start without `SECRET_KEY` in `.env` (gitignored, never baked into the image). Create it once per machine: `printf 'SECRET_KEY=%s\n' "$(openssl rand -hex 32)" > .env`. Changing it logs everyone out; private URLs are unaffected.
- `DEBUG=0` in `docker-compose.yml`: the site is public, so no tracebacks. Set it to 1 locally only when debugging.
- All services have `restart: unless-stopped`, so they come back after a crash or reboot (as long as Docker itself starts).
- Source is copied into the image at build time, not mounted. Rebuild (`docker compose up -d --build`) before running tests or checking pages, or the container runs old code.
- The image installs only non-dev Python packages, so test modules that import `selenium` fail to load (`No module named 'selenium'`). Install it in the running container first: `docker compose exec web pip install selenium`.

## Current status (as of 2026-10-04)

Done:
- Fork runs in docker compose (web, worker, db, redis) at http://localhost:8000 on the test PC.
- Dockerfile fails loudly on bad downloads (`d591509bd`). User-facing name is RoparCat (`4c773db69`); Tabbycat credited in footer and meta description.
- Public via Tailscale Funnel at https://roparcat.tailcee4ed.ts.net/. nginx forwards `X-Forwarded-Proto` and `docker.py` sets `SECURE_PROXY_SSL_HEADER`, so absolute links (private URLs, emails) are `https://` (`386a14ca4`).
- Hardened for public hosting (`056d9f345`): `SECRET_KEY` from `.env`, `DEBUG=0`, `restart: unless-stopped`, `*.dump` ignored. Pushed to `origin/develop`.
- Email over SMTP (`573f22ff4`): settings come from `.env`. Active on AWS (new app password, SMTP login verified 2026-10-04); not on the test PC.
- Test tournaments in the `pgdata` volume:
  - `australs24team`: demo, rounds 1-3 simulated, public draw/standings/tabs on.
  - `apd8team`: dummy APD (UADC preset), 8 teams x 3 speakers, 5 adjs, 1 round (Round 1 draw released), private URLs for everyone. Public draw on ("all released rounds", `/apd8team/draw/round/<n>/`); every other public page off. Keys live in `Person.url_key`; never run `privateurls generate --overwrite` (breaks shared links).

## Production: AWS EC2 (live since 2026-10-04, until the user shuts it down, around 2026-10-08)

The test PC is only for development. Production runs on one EC2 instance, reached through the same Funnel URL.

Deployed 2026-10-04: `m7i-flex.large` (2 vCPU, 7.6 GB, 105 GB disk), Ubuntu 26.04, region `ap-southeast-2` (Sydney, not Mumbai: about 150 ms from India, acceptable). SSH as `ubuntu` to the instance's public IP (EC2 console; kept out of this public repo) with the `eristic26.pem` key (kept in `~/.ssh` on the test PC). Code in `~/roparcat` on `develop`; DB restored from the test PC (both tournaments, all 29 `apd8team` keys). Tailscale node `roparcat`, Funnel on 8000. Hourly `pg_dump` cron into `~/backups/`. The old Windows node was renamed/removed; until its Tailscale is quit or reconnects, the test PC resolves the URL to itself and fails (other devices are fine).

Checked 2026-10-04: port 8000 not reachable from the internet (security group closed; only Funnel serves the site), Funnel on, email settings loaded and SMTP login OK, backup cron command tested under cron's environment (first run on the next UTC hour), no automatic reboots configured, one superuser.

Still to do (user):
- Send a test email from the home page tool while logged in via the Funnel URL.
- Revoke the first app password (see Other open items).
- Open the site from a phone on mobile data.
- Tailscale key for `roparcat` expires 2027-04-01: no risk for this event, but disable key expiry if the server will be kept.
- Quit Tailscale on the test PC (or `tailscale down`); it still resolves the URL to its old address.
- Set an AWS budget alert if not done.
- `scp` the newest `~/backups/*.dump` to a PC after each round.

How it was set up:

- Account: new-style AWS Free plan ($100+ credits, 6 months; the old 12-month free tier no longer exists). Region `ap-south-1` (Mumbai). Set a budget alert.
- Instance: Ubuntu 24.04, free-tier-eligible with >= 2 GB RAM (`t3.small` + 2 GB swap, or `m7i-flex.large`), 30 GB gp3. Security group: SSH from "My IP" only; no other ports (Funnel is outbound).
- Steps:
  1. Install Docker (`curl -fsSL https://get.docker.com | sudo sh`, add `ubuntu` to the `docker` group).
  2. `git clone https://github.com/roparcat/roparcat.git && git checkout develop`.
  3. Create a fresh `.env` with `SECRET_KEY` (see Docker gotchas) plus the `EMAIL_*` lines (see Other open items). Never copy the test PC's key.
  4. Move the DB: on the test PC `pg_dump -Fc -f /tmp/roparcat.dump` inside `db`, `docker compose cp` it out, `scp` it up. On the server `docker compose up -d db`, copy it in, `pg_restore --clean --if-exists --no-owner`, then `docker compose up -d --build`. Check `/apd8team/privateurls/rgl1014x/` returns 200 (proves keys survived). Don't redirect the dump with `>` in PowerShell, it corrupts it.
  5. Tailscale: `tailscale funnel reset` on the old machine, remove/rename it in the admin console so the name `roparcat` is free, then on the server `tailscale up --hostname=roparcat` and `tailscale funnel --bg 8000`. Disable key expiry for the node. Test from a phone on mobile data.
  6. Hourly backups via cron (`docker compose exec -T db pg_dump -U tabbycat -Fc tabbycat > ~/backups/...`); `scp` them down after each round.
  7. Shutdown is manual: the user stops/terminates the instance themselves after taking the final backup. Never schedule automatic shutdowns.
- After cutover, the EC2 copy is the live one. Changes on the test PC don't carry over.

## Planned: new RoparCat icon

Replace the Tabbycat cat logo with a RoparCat one. Keep the Tabbycat credit in the footer (AGPL rule above).

Where the icon lives (all under `tabbycat/`):
- `templates/nav/logo.html`: inline SVG used in the top nav (33px) and admin sidebar (18px). Uses `{{ width }}` and `{{ alt }}`; keep those.
- `templates/nav/logo_local.html` and `static/logo-local.svg`: variant shown only when `ON_LOCAL` (not in docker). Replace too or delete.
- `static/logo.svg` (also the API docs logo, `settings/core.py` `x-logo`), `static/logo-16x16.png`, `logo-32x32.png`, `logo-48x48.png`, `static/root/favicon.ico`, `static/safari-tab.svg` (single-colour mask icon), `static/logo-social.png` (og:image link previews).
- `templates/base.html`: `<link rel="icon">` tags; `mask-icon` colour is hardcoded `rgb(102, 61, 160)`.

Plan:
1. Get the new design as one square SVG (works at 16px, readable as a single colour for `safari-tab.svg`).
2. Export the PNG sizes, the `.ico` (16/32/48 in one file) and a 1200x630 `logo-social.png`.
3. Swap the files keeping the same names, so no template changes beyond `logo.html`'s inline SVG and the mask colour.
4. Rebuild, check tab icon, nav, admin sidebar, and a link preview. Browsers cache favicons hard; test in a private window.

## Planned: minor colour scheme and layout changes

Colours (SCSS, compiled at image build, so rebuild to see changes):
- Brand/primary: `$purple: #663da0` in `templates/scss/components/custom.scss` (Bootstrap theme colours: `$green`, `$blue`, `$orange`, `$red` are beside it). Changing `$purple` recolours buttons, links and highlights site-wide.
- Same purple is hardcoded in `templates/base.html` (mask-icon), `templates/nav/logo.html` (gradient) and `checkins/templates/CheckInScanContainer.vue` (QR scan outline). Update them to match.
- Layout colours: `templates/scss/components/variables.scss` (`$sidebar-bg: #333c47`, table hover, navbar/footer background and border).
- Leave the gender/break/region/conflict/ranking colours in `variables.scss` alone; they encode meaning in the allocation UI.

Layout (keep it minor):
- Nav and sidebar: `templates/scss/modules/nav.scss`, `templates/nav/*.html`. Footer: `templates/scss/modules/footer.scss` (keep the Tabbycat credit). General spacing: `modules/layout.scss`, type: `modules/typography.scss`, fonts: `$font-family-sans-serif` in `custom.scss`.

Plan:
1. Pick the new palette (primary + maybe sidebar colour) and check text contrast (WCAG AA) on buttons and the sidebar.
2. Change the variables first. Only touch module SCSS for real layout changes.
3. Rebuild and check public pages, the admin draw and allocation pages, private URL pages and printables (`templates/scss/printables.scss`) on desktop and phone width.
4. Don't do this while the tournament is live (2026-10-03 to 08) unless it's tested on the test PC first; a rebuild restarts the site.

## Other open items
- REMINDER: revoke the first `debsoc@iitrpr.ac.in` app password (it was pasted in a chat on 2026-10-03) in the Google account (Security > App passwords). The AWS server already uses a different, new app password (checked), and the old lines were deleted from the test PC's `.env`, so revoking breaks nothing.
- Test PC (2026-10-04): C: filled up during a rebuild and crashed Docker; data was fine and the site came back via `restart: unless-stopped`. Rebuilds then failed on a flaky connection (pypi timeouts), so the test PC still runs the image from before `573f22ff4`: email is not active there. Email gets enabled and tested on AWS instead. Watch free disk space before rebuilding (`docker builder prune -af` frees build cache; the volume is untouched).
- Email: SMTP via the society account `debsoc@iitrpr.ac.in` (Google Workspace, app password). `docker.py` reads `DEFAULT_FROM_EMAIL`, `EMAIL_HOST` (`smtp.gmail.com`), `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT` (587), `EMAIL_USE_TLS` from `.env` (compose passes `.env` to web and worker via `env_file`); without `EMAIL_HOST` no email is sent. The password lives only in `.env`, never in git. Each server needs these lines in its own `.env`. No `apd8team` participant has an email address yet. Send emails while browsing via the Funnel URL, not localhost, since links are built from the request host.
- APD test: Round 1 draw is released. Still: decide on the "Use Private URLs" preset (ballot and feedback via private links). Only Round 1 exists; add rounds in Edit Database.
- Port 8000 is published on `0.0.0.0`; with Funnel it could be bound to `127.0.0.1`.
- Decide on the upstream donation text, the "Our Organisation" footer block, the 500 page bug-report links, and `ADMINS` in `tabbycat/settings/core.py`.
- 5 apps on `develop` (actionlog, checkins, participants, results, users) have model changes with no migration (pre-existing, from upstream).
