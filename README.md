# Weather Aware Truck Routing

A React and Django web app that helps a truck driver pick the safest route based on weather, load weight and travel time.

The driver enters an origin, a destination, a departure time and a load weight. The app generates three routes, samples weather along each one at the driver's estimated arrival time, rates every checkpoint, recommends one route and draws everything on a map with a 0 to 48 hour weather heatmap.

## Features

- Three route options per trip
- Weather sampled every 10, 25 or 50 miles, read at the truck's estimated arrival time at each checkpoint
- Wind, rain and snow risk classification plus load weight rules
- Recommendation ranked by severe miles, high miles, average risk and travel time, with a plain language reason
- Map with all routes, risk coloured checkpoints, ETAs, tooltips and route summaries
- Heatmap along the trip corridor with a 0 to 48 hour forecast slider

## Stack

| Area | Choice |
|---|---|
| Backend | Django 5.2, Django REST Framework |
| Frontend | React 19, TypeScript, Material UI, Leaflet, leaflet.heat |
| Routing | OSRM public API (no key) |
| Geocoding | Nominatim (no key) |
| Weather | Open-Meteo hourly forecast, with MET Norway as an automatic fallback (no keys) |
| Cache | Django cache, Redis when `REDIS_URL` is set, in memory otherwise |

No API keys are needed to run the project.

## Run locally

Backend

```
cd backend
python3.13 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
DJANGO_DEBUG=true python manage.py runserver 8000
```

Frontend

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend calls http://localhost:8000 by default. Set `VITE_API_URL` to change it.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | development value | Django secret key, set it in production |
| `DJANGO_DEBUG` | `false` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma separated hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Comma separated frontend origins |
| `REDIS_URL` | unset | Enables the Redis cache |
| `OSRM_BASE_URL` | public OSRM | Routing service |
| `GEOCODER_URL` | public Nominatim | Geocoding service |
| `GEOCODER_USER_AGENT` | `truck-weather-routing/1.0` | Required by the Nominatim usage policy |
| `WEATHER_URL` | Open-Meteo forecast | Primary weather service |
| `METNO_URL` | MET Norway locationforecast | Fallback weather service |
| `WEATHER_USER_AGENT` | project name and repository | Identifies the app to MET Norway, which requires it |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL used by the frontend build |

## API

`POST /api/plan/`

```
{
  "origin": "Chicago, IL",
  "destination": "Dallas, TX",
  "departure": "2026-10-15T08:00:00Z",
  "load_lb": 42000,
  "spacing_miles": 25
}
```

`departure` must fall within the next 48 hours. `load_lb` is 0 to 120000. `spacing_miles` is 10, 25 or 50 and defaults to 25.

The response contains the geocoded origin and destination, the recommendation, every route with its checkpoints and summary, and the heatmap data. Validation problems return 400, unknown places and unroutable trips return 422, and upstream failures return 502.

`GET /api/health/` returns `{"status": "ok"}`.

## Architecture

```
backend/trips
  domain/     pure logic, no I/O
    thresholds.py   risk bands and load rules as data
    risk.py         classify weather and apply load rules
    sampling.py     checkpoints along a route and their ETAs
    ranking.py      route summaries, ordering, decisive criterion
    geo.py          distance, interpolation, offsets
    weather.py      hourly series and nearest hour lookup
  clients/    one small module per external service
  services/   planner that orchestrates the whole trip
  serializers.py  input validation
  presenters.py   response shaping
  views.py        thin endpoints

frontend/src
  api/        typed client
  features/trip/   form, results, route cards, checkpoint table
  features/map/    map, route layers, heatmap, slider, legend
  lib/        formatting and risk presentation
```

The risk engine and the ranking are pure functions, so they are covered by unit tests without any network access.

## Risk rules

| Condition | Low | Moderate | High | Severe | No travel |
|---|---|---|---|---|---|
| Wind (mph) | under 25 | 25 to 34 | 35 to 44 | 45 to 54 | 55 or more |
| Rain (in/hr) | under 0.10 | 0.10 to 0.25 | 0.25 to 0.50 | 0.50 to 1.00 | over 1.00 |
| Snow (in/hr) | under 0.5 | 0.5 to 1.0 | 1.0 to 2.0 | 2.0 to 3.0 | over 3.0 |

Load rules can only raise the level

- Wind of 55 mph or more is No Travel for any load
- Wind of 45 to 54 mph with a load over 30,000 lb is No Travel
- Wind of 35 to 44 mph with a load over 40,000 lb is Severe

A checkpoint takes the worst of its wind, rain, snow and load adjusted levels.

## Decisions and assumptions

- Boundary values that two bands share, such as exactly 0.25 in/hr of rain, fall into the higher band. Rain and snow No Travel use strictly greater than, exactly as the thresholds are written.
- Wind uses the sustained 10 metre wind speed, not gusts.
- Miles are weighted by the stretch each checkpoint represents, not by checkpoint count. Each checkpoint covers the ground from the midpoint before it to the midpoint after it.
- Route ranking order is fewest severe miles, fewest high miles, lowest average risk, shortest time. A route with any No Travel checkpoint ranks after every route without one. If every route is blocked, the app says so instead of presenting a safe choice.
- ETAs scale the routing API duration by distance along the route. OSRM uses car speeds, so truck times are optimistic.
- The routing API often returns fewer than three alternatives. When it does, the backend asks for extra routes through offset waypoints and keeps only those that differ enough from the routes already found.
- The heatmap uses the checkpoints of all three routes. The backend sends 49 hourly risk levels for each point once, and the slider only switches frames in the browser, so moving it never triggers a request.
- Forecast data is fetched in batches, snapped to a 0.01 degree grid and cached for 30 minutes. Geocoding is cached for a day and routes for an hour.
- Open-Meteo limits free usage per IP address, and shared hosting addresses regularly exhaust the daily quota. When Open-Meteo refuses a request, the backend falls back to MET Norway, which is limited per application instead. MET Norway reports precipitation amounts and a symbol such as rain, sleet or snow. Snow is converted to snowfall at the standard 10 to 1 snow to liquid ratio and sleet is split evenly between rain and snow.
- Departure must be within the next 48 hours because the forecast slider covers 0 to 48 hours and weather is only reliable in that window.
- Public OSRM and Nominatim servers are rate limited and meant for light use. Point `OSRM_BASE_URL` and `GEOCODER_URL` at your own instances for real traffic.

## Quality

```
cd backend && ruff check . && ruff format --check . && pytest
cd frontend && npm run lint && npm run format:check && npm run typecheck && npm test
```

The code base has no comments, no docstrings and no console output by design. Names carry the meaning.
