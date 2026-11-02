# Edesur for Home Assistant

Unofficial Home Assistant integration for Edesur Argentina. **Work in progress**; not yet installable.

## Features planned
- Account authentication with a selectable login method.
- **Google/social login**: first supported method (observed and used successfully by the project owner).
- **Username/password** and other login methods: visible as future options, **not implemented** until their API flows are understood.
- Automatic discovery of multiple contracts linked to the account.
- Meter information, historical readings, invoices, payments, supply status and debt, subject to API validation.

## Development status
API research and integration scaffolding. Authentication has been observed working in the browser/Postman workflow; Home Assistant's end-to-end login is not implemented yet. Google social login is not the same thing as implementing Google's OAuth protocol independently.

## Authentication design
The future Home Assistant config flow will start with a **login method selector**. Only Google will be enabled initially. Unsupported methods will be labeled as pending rather than attempting authentication. Authentication logic will be isolated from the account/sensor layers to support future methods.

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

## Architecture principles
Follow Home Assistant patterns: a dedicated async API client, `DataUpdateCoordinator`, config flow, separate sensor descriptions and tests with sanitized fixtures. Comment non-obvious blocks and API quirks, not every line. Never store credentials or tokens in Git, debug logs, documentation, committed JSON or diagnostics.

## Branches
All work goes to `dev`. The repository owner alone promotes reviewed changes to `main`.

## License
[GNU General Public License v3.0](LICENSE).

Not affiliated with Edesur.
