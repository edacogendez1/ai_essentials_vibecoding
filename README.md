# Flight price tracker

Watches flight routes and notifies you when a price hits a new **all-time low** (lowest ever recorded by this tracker). Python 3, no dependencies.

```
python -m flighttracker add ORD LHR 2027-01-10 --return-date 2027-01-20
python -m flighttracker check --provider mock          # try it with fake prices
python -m flighttracker watch --provider amadeus --notify ntfy --interval 3600
python -m flighttracker list | history 1 | remove 1
```

- **Prices:** `amadeus` (free API key from developers.amadeus.com: `AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET`; `AMADEUS_ENV=production` for live fares) or `mock`.
- **Notifications:** `console`, `ntfy` (phone push, set `NTFY_TOPIC`), `email` (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO`).
- Alerts start after `--min-history` checks (default 3) so early checks don't all count as "lows". "All-time" means since you started tracking.

Notebook: open `flight_tracker.ipynb` from the repo root (needs `jupyter`; the chart needs `matplotlib`).

Tests: `python -m unittest discover tests`
