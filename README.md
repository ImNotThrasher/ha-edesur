# Edesur for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom%20repository-blue.svg)](https://www.hacs.xyz/)

**Unofficial, community-maintained Home Assistant integration** for Edesur Argentina.

Edesur (Empresa Distribuidora de Energía Sur Sociedad Anónima) is an electricity distributor serving part of the Buenos Aires metropolitan area in Argentina. This integration aims to make information about your Edesur electricity accounts available in Home Assistant.

> [!IMPORTANT]
> This project is **not an official Edesur integration** and is not developed, endorsed, supported, or affiliated with Edesur. It uses an undocumented API that may change without notice.
>
> **Development status:** experimental. Manual installation and account discovery have been tested on a running Home Assistant instance; the new historical sensors still require validation.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Entities](#entities)
- [Limitations](#limitations)
- [Privacy and security](#privacy-and-security)
- [Contributing](#contributing)
- [License and trademarks](#license-and-trademarks)

## Features

Currently implemented:

- Google/social account login using a manually supplied Edesur social identifier.
- Automatic discovery of multiple electricity contracts linked to an account.
- Periodic refresh of account data.
- Sensors for linked contracts and meter numbers.
- Per-contract sensors for latest consumption and meter reading, reading date, latest invoice amount and dates, latest payment amount and date, and supply status.

Historical API responses are queried; latest values are exposed as sensors. Debt status is available when the API explicitly reports no debt or returns a nonempty debts list; amounts and per-invoice paid status are not inferred. Formality status is also exposed.

## Installation

HACS listing is **not available yet**. For testing, add this repository as a custom integration repository in HACS, select **Integration**, and install it. Restart Home Assistant after installation.

Alternatively, copy `custom_components/edesur` into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

1. Sign in to the [Edesur online portal](https://ov.edesur.com.ar/) using your Google account.
2. In your browser's developer tools (DevTools), inspect the Edesur social-login request and locate its `socialMediaId` value (starting with `google_`).
3. In Home Assistant, open **Settings → Devices & services → Add integration**, search for **Edesur**, and select **Google (manual identifier)**.
4. Enter the email address associated with your Edesur account and the complete `socialMediaId`.

The integration uses these values to request an Edesur session token and discover linked contracts. **You do not need to create a Google Cloud project.** A built-in Google OAuth login is not implemented.

Keep the social identifier private. Never share access tokens, browser cookies, or complete login requests.

## Entities

The integration defines:

| Entity | Description |
| --- | --- |
| Linked contracts | Number of contracts associated with the account |
| Meter number | Meter identifier for each discovered contract, when available |
| Latest consumption and reading | Most recent API-reported active consumption and cumulative reading (active consumption in kWh; cumulative reading unit not yet confirmed) |
| Last reading date | Date of the latest meter reading |
| Latest invoice | Amount in ARS, issue date, first and second due dates |
| Latest payment | Amount in ARS and payment date |
| Supply status | Raw status reported by Edesur |

Sensors are created separately for each contract. Invoice number and payment method are exposed as limited attributes. Download URLs are not exposed.

## Limitations

- **Experimental:** newly added sensors still require live validation.
- Only the manual Google/social identifier method is implemented; email/password login is not supported.
- Edesur's undocumented API can change or become unavailable.
- The integration does not control electricity supply, make payments, or modify account details.
- Only the latest reading, invoice and payment are exposed; full history is not yet modeled as statistics or entities.
- Period consumption (`activeConsumption`) is confirmed in kWh and exposed as an energy sensor without `total_increasing` state class. Cumulative meter reading (`activeReading`) still needs separate unit and semantics verification.
- The legacy debt endpoint requires an unresolved `supply_number` distinct from the contract account; its request and identifier mapping are not verified.
- Outstanding balance, whether an invoice is unpaid, and overdue debt cannot be inferred reliably from invoice dates or payment history; no debt or unpaid-status sensor is provided.
- `remainingConsumption` and peak/night reading semantics remain unverified and are not exposed.

## Privacy and security

The integration communicates with Edesur to access the account information required for its sensors. Your email and social identifier are stored in Home Assistant's integration configuration; the session token is kept in memory by the API client. Treat your Home Assistant backups as sensitive.

This is an independent, unofficial project. Use it at your own risk.

## Contributing

Bug reports and contributions are welcome through [GitHub Issues](https://github.com/ImNotThrasher/ha-edesur/issues). Technical API research and the sanitized Postman collection are available in [docs](docs/).

## License and trademarks

The source code is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See [LICENSE](LICENSE).

**Edesur** and any associated names, trademarks, service marks, and logos are the property of their respective owners. This is an independent, community-developed project and is **not affiliated with, endorsed by, sponsored by, or officially supported by Edesur**. References to Edesur are for identification and compatibility purposes only. The software license does not grant permission to use third-party trademarks or logos.

## Debt and formalities

The integration queries `GET /PlanPagos/get-debts` with `contractAccount`, `serchType=1` and `value` for each account. An explicit no-debt message is mapped to **Sin deuda registrada**. A nonempty `debts` array is mapped to **Deuda registrada**, without inferring the amount or invoice-level payment state. Unrecognized responses remain unknown. `GET /Cliente/get-formalities` exposes the most recent formality status/date and minimal metadata. Period consumption history (up to 36 readings) is available as a sensor attribute for dashboard charts; this is not a Home Assistant long-term statistics series.
