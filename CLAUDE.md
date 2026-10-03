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

## Current status / next steps (as of 2026-10-03)

Done:
- Fork runs locally in docker compose (web, worker, db, redis) at http://localhost:8000.
- Dockerfile fix committed (`d591509bd`): `pipefail` + `curl -fsSL` so a failed nvm download stops the build instead of causing `nvm: command not found` later.
- User-facing name changed to RoparCat (`4c773db69`); Tabbycat credited in footer and meta description.
- Local DB has two test tournaments (live in the `pgdata` volume, survive reboot):
  - `australs24team`: demo, rounds 1-3 simulated, public draw/standings/tabs on.
  - `apd8team`: dummy APD (UADC preset), 8 teams x 3 speakers, 5 adjs, 1 round (no draw yet), private URLs generated for everyone, all public pages off. Keys are stored in the DB (`Person.url_key`), so the links survive reboot; `privateurls generate --overwrite` would replace them and break any already shared.

- Public via Tailscale Funnel at https://roparcat.tailcee4ed.ts.net/. nginx forwards `X-Forwarded-Proto` and `docker.py` sets `SECURE_PROXY_SSL_HEADER`, so absolute links (private URLs, emails) come out as `https://`.
- `apd8team` public draw set to "all released rounds" (`/apd8team/draw/round/<n>/`); everything else public stays off.

Next:
- Port 8000 is published on `0.0.0.0`, so it's also reachable on the LAN; with Funnel (proxies from localhost) it could be bound to `127.0.0.1`.
- Email: no provider configured, and `docker.py` reads no `EMAIL_*` settings yet (copy the block from `heroku.py`, secrets in `.env`). No `apd8team` participant has an email address. Send emails while browsing via the Funnel URL, not localhost, since links are built from the request host.
- For the APD test: generate and release the Round 1 draw; decide whether to apply the "Use Private URLs" preset (ballot and feedback entry via private links). Only Round 1 exists; add more rounds in Edit Database.
- Decide what to do with the upstream donation text, the "Our Organisation" footer block, the 500 page bug-report links, and `ADMINS` in `tabbycat/settings/core.py`.
- 5 apps on `develop` (actionlog, checkins, participants, results, users) have model changes with no migration (pre-existing, from upstream).
