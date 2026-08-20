# Mindicator MCP

FastMCP HTTP server over `mumbai_mindicator.sqlite` (Mumbai transit offline dump).

## Tools

| Tool | Title | Purpose |
|------|-------|---------|
| `health_check` | Check Health | Service + DB meta |
| `get_schema` | List Database Tables | Full table/column catalog |
| `execute_sql` | Run SQL Query | Read-only `SELECT` / `WITH` (LIMIT capped) |
| `get_live_status` | Live Train Status | Live running status for a train number |
| `search_stations` | Search Train Stations | Find stations by name |
| `find_train_path` | Find Train Path | Path hints between two stations |
| `get_ticket_fare` | Get Ticket Fare | Suburban OD ticket fares |
| `search_bus_routes` | Search Bus Routes | Find bus routes by code/agency |
| `get_bus_route_stops` | Get Bus Route Stops | Ordered stops on a route |
| `get_auto_fare` | Get Auto Fare | Auto rickshaw day/night fare by km |

## Setup

```bash
uv sync
uv run init.py
```

Copy `.env.example` to `.env` if you want to override defaults.

## Run

```bash
uv run mindicator-mcp
```

Listens on `http://127.0.0.1:8000` by default (`HOST` / `PORT` in `.env`).

## Docker

```bash
docker build -t mindicator-mcp .
docker run --rm -p 8000:8000 mindicator-mcp
```

MCP URL: `http://127.0.0.1:8000/mcp`

## Cursor MCP config (HTTP)

```json
{
  "mcpServers": {
    "mindicator": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Start the server first (`uv run mindicator-mcp`), then use Cursor.

## Demo notebook (smolagents chatbot)

Beginner walkthrough: explanations + small code cells →  
[`notebooks/mindicator_smolagents_demo.ipynb`](notebooks/mindicator_smolagents_demo.ipynb)

```bash
uv sync --extra demo
uv run mindicator-mcp   # terminal 1 — leave running
```

Then open the notebook in Cursor/VS Code and pick the project `.venv` as the kernel.  
Set `OPENAI_API_KEY` in `.env` (or paste when the notebook prompts you).

## Sample prompts

- How do I get from Churchgate to Thane on the local?
- Auto fare for 5 km at night
- Stops on BEST bus route `1(Up)`
- Trains after 09:00 at Dadar on the Central line
- Is train 95338 running late right now?

## Sample SQL (via `execute_sql`)

```sql
SELECT from_station, to_station, path_desc
FROM transfer_paths
WHERE from_station = 'CHURCHGATE' AND to_station = 'THANE'
LIMIT 5;
```

```sql
SELECT src_station, dst_station, route_code, fare_1, fare_6
FROM ticket_fares
WHERE src_station = 'CHURCHGATE' AND dst_station = 'THANE'
LIMIT 10;
```

## Layout

- `app/main.py` — FastMCP wiring
- `app/service` — business logic + `APIResponse`
- `app/repository` — SQLite only
- `app/integrations` — third-party HTTP clients (live trains)
- `app/domain/schemas` — pydantic models
- `app/core` — config, exceptions, logging
