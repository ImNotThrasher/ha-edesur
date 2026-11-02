# Edesur for Home Assistant

Unofficial Home Assistant integration for Edesur Argentina. **Work in progress**; experimental and not validated against a live Home Assistant instance.

## Features planned
- Account authentication with a selectable login method.
- **Google/social login**: first supported method (observed and used successfully by the project owner).
- **Username/password** and other login methods: visible as future options, **not implemented** until their API flows are understood.
- Automatic discovery of multiple contracts linked to the account.
- Meter information, historical readings, invoices, payments, supply status and debt, subject to API validation.

## Development status
Initial Home Assistant config flow, API client, polling coordinator, and discovery sensors are implemented but **not yet validated against live credentials or a running Home Assistant instance**. The current Google/social flow requires a manually supplied social identifier; a native Google sign-in flow remains pending. Google social login is not the same thing as implementing Google's OAuth protocol independently.

## Authentication design
The Home Assistant config flow starts with a **login method selector**. Only Google is enabled initially. Unsupported methods will be labeled as pending rather than attempting authentication. Authentication logic will be isolated from the account/sensor layers to support future methods.

## API research
The single consolidated Postman collection lives in `docs/postman/Edesur.postman_collection.json`. It uses placeholders such as `{{social_email}}`, `{{social_id}}` and `{{bearer_token}}`; fill these through **local Postman variables/environments**, never committed files.

Endpoints under `https://ed.edesur.com.ar/api`:
- `POST /Usuario/login-social-media` — Google/social login request.
- `GET /Cliente/supply-retrieve/{social_email}` — discover contracts.
- `GET /Cliente/get-client/{client_id}` — contract details.
- `GET /Cliente/get-historical-readings/{client_id}` — readings.
- `GET /Cliente/get-historical-invoices/{client_id}` — invoices.
- `GET /Cliente/get-historical-payments/{client_id}` — payments.
- `GET /Cliente/get-cut-supply/{client_id}` — supply status.
- `POST /PlanPagos/GetDeudaAsync` — debt; HTTP method still needs confirmation.

## Current entities

- Number of linked contracts.
- Meter number per contract (when returned by the API).

Historical consumption, invoices, payments, debt and due dates are **not yet mapped to entities**: their response schemas need validation. The coordinator currently fetches the four known read-only endpoints for each contract. Debt is available only as an experimental Postman/API-client operation.

## Architecture principles
Follow Home Assistant patterns: a dedicated async API client, `DataUpdateCoordinator`, config flow, separate sensor descriptions and tests with sanitized fixtures. Comment non-obvious blocks and API quirks, not every line. Never store credentials or tokens in Git, debug logs, documentation, committed JSON or diagnostics.

## Branches
All work goes to `dev`. The repository owner alone promotes reviewed changes to `main`.

## License
[GNU General Public License v3.0](LICENSE).

Not affiliated with Edesur.
