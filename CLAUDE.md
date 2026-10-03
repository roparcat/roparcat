# RoparCat

RoparCat is a fork of Tabbycat for IIT Ropar debate tournaments.

## Rules

- The license is AGPL-3.0. Never remove copyright notices or Tabbycat credits.
- We run everything through docker compose. Use `docker compose exec web python tabbycat/manage.py ...` for management commands (the container's working directory is `/tcd`; `manage.py` lives in `tabbycat/`).
- Run the relevant tests after every change to draw, results, or standings code:
  `docker compose exec web python tabbycat/manage.py test draw results standings --exclude-tag=selenium --noinput`
- Never commit or push without showing me the diff first.

## Docker gotchas

- Source is copied into the image at build time, not mounted. Rebuild (`docker compose up -d --build`) before running tests or checking pages, or the container runs old code.
- The image installs only non-dev Python packages, so test modules that import `selenium` fail to load (`No module named 'selenium'`). Install it in the running container first: `docker compose exec web pip install selenium`.
