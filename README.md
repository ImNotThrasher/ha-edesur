# Edesur for Home Assistant

[![Latest release](https://img.shields.io/github/v/release/ImNotThrasher/ha-edesur?label=release)](https://github.com/ImNotThrasher/ha-edesur/releases/latest)
[![Validation](https://github.com/ImNotThrasher/ha-edesur/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/ImNotThrasher/ha-edesur/actions/workflows/validate.yml)
[![GitHub downloads](https://img.shields.io/github/downloads/ImNotThrasher/ha-edesur/total)](https://github.com/ImNotThrasher/ha-edesur/releases)
[![HACS custom repository](https://img.shields.io/badge/HACS-custom%20repository-41BDF5)](https://www.hacs.xyz/)
[![GitHub stars](https://img.shields.io/github/stars/ImNotThrasher/ha-edesur?style=flat)](https://github.com/ImNotThrasher/ha-edesur/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/ImNotThrasher/ha-edesur)](https://github.com/ImNotThrasher/ha-edesur/issues)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

[![Open repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ImNotThrasher&repository=ha-edesur&category=integration)
[![Add integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=edesur)

**Unofficial Home Assistant integration for Edesur Argentina.** Read electricity-account information, invoices, payments, meter readings, debt and supply status, and historical consumption from the Edesur online portal.

> [!IMPORTANT]
> This is an independent community project, **not affiliated with, endorsed by, or supported by Edesur**. It relies on an undocumented API that can change without notice. The integration is experimental; not every feature has been independently tested across multiple accounts or installations.

## Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Installation](#installation)
- [Authentication: find your socialMediaId](#authentication-find-your-socialmediaid)
- [Entities and historical statistics](#entities-and-historical-statistics)
- [Updating an existing installation](#updating-an-existing-installation)
- [Limitations](#limitations)
- [Privacy and security](#privacy-and-security)
- [Development](#development)
- [License and trademarks](#license-and-trademarks)

## Features

- Google/social login using the Edesur portal's `socialMediaId` and account email, or standard Edesur email/password login (response format pending live verification).
- Automatic discovery of multiple electricity contracts linked to the same account.
- Periodic cloud polling and automatic reauthentication on each update.
- Separate Home Assistant devices and sensors per contract.
- Latest period consumption (kWh), latest cumulative meter reading and its date.
- Latest invoice amount (ARS), issue date, and first/second due dates.
- Latest payment amount and payment date.
- Supply status, debt status, payment agreement status, and latest formality status/date.
- Historical consumption readings imported as **external long-term statistics** for native Home Assistant statistics graphs.

**Read-only:** the integration does not pay invoices, modify account details or control electricity supply.

## Screenshots

The screenshots below show an example Home Assistant dashboard with multiple Edesur supplies and the entities created by the integration. The dashboard is a user-configured Lovelace view, **not** a dashboard automatically installed by Edesur.

### Electricity dashboard

![Home Assistant electricity dashboard showing supplies, invoice information and historical consumption](docs/images/edesur-dashboard.jpg)

### Integration entities

![Home Assistant Edesur device entities and sensor states](docs/images/edesur-entities.jpg)

> Screenshots are illustrative. Available entities and values depend on the Edesur account and the data returned by its API.

## Requirements

- Home Assistant with support for custom integrations.
- An Edesur online account linked to one or more electricity contracts.
- Access to the [Edesur online portal](https://ov.edesur.com.ar/) using **Sign in with Google** or a traditional Edesur account.
- Your account email and either an Edesur password or a `socialMediaId` obtained from your own browser session (instructions below).
- Internet connectivity from Home Assistant to Edesur's service.

## Installation

### Recommended: HACS

1. In Home Assistant, open **HACS → Integrations → Explore & Download Repositories**.
2. Search for **Edesur**, open the integration, and select **Download**.
3. Follow the restart prompt, if shown.
4. For Google login, obtain your `socialMediaId` as described in [Authentication](#authentication-find-your-socialmediaid).
5. Click **Add Integration** below, or open **Settings → Devices & services → Add integration**, search for **Edesur**, select **Google (social login)** or **Email and password**, and enter the corresponding credentials.

[![Add integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=edesur)

### HACS custom repository fallback

[![Open repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ImNotThrasher&repository=ha-edesur&category=integration)

If Edesur does not appear in HACS search yet, add it as a custom repository:

1. Click **Open repository in HACS** above. Alternatively, open **HACS → three-dot menu → Custom repositories** and enter `https://github.com/ImNotThrasher/ha-edesur` with type **Integration**.
2. Download Edesur from HACS and follow any restart prompt.
3. For Google login, obtain your `socialMediaId` using the [Authentication](#authentication-find-your-socialmediaid) instructions.
4. Add **Edesur** under **Settings → Devices & services → Add integration** and complete the configuration form.

The repository has been accepted into the default HACS catalog, but it may take time for updated catalog data to reach individual installations. The buttons open your own Home Assistant instance; they do not install anything by themselves. The integration includes a local `brand/icon.png` for Home Assistant 2026.3+; depending on your HACS version, its repository listing may still show a placeholder icon.

### Manual installation

1. Download the [latest release](https://github.com/ImNotThrasher/ha-edesur/releases/latest).
2. Copy the complete `custom_components/edesur` directory into the `custom_components` folder in your Home Assistant configuration directory.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration → Edesur** and complete the setup.

Manual installation works without HACS, but updates must be installed manually. **Do not install both ways independently or delete an existing configuration entry when switching methods.** See [updating an existing installation](#updating-an-existing-installation).

## Authentication: find your socialMediaId

Edesur supports Google/social authentication through a **manually supplied identifier** and traditional Edesur username/password authentication. Select the method matching your Edesur account. The integration does not implement Google's OAuth flow and does not ask for your Google password. The standard login endpoint's successful response format has not yet been independently verified.

1. Open [https://ov.edesur.com.ar/](https://ov.edesur.com.ar/) in your browser.
2. Open **Developer Tools** (usually **F12**) and select the **Network** tab. Enable **Preserve log** if the login redirects or reloads the page.
3. Sign in to Edesur using **Google** with your own account.
4. In Network, filter requests by `login-social-media`. Select the request to `/Usuario/login-social-media`.
5. Open the **Payload** (or **Request payload**) panel. Locate the field named **`socialMediaId`**, whose value begins with `google_`.
6. Copy **only the complete value** of `socialMediaId` and enter it, along with the email associated with your Edesur account, in the Home Assistant integration setup.

Example of the *field names only* (the value below is fictional):

```json
{
  "socialMediaEmail": "your-email@example.com",
  "socialMediaId": "google_EXAMPLE_DO_NOT_USE"
}
```

**Never share the actual request payload, browser network export, authentication token, cookies, or social ID.** Treat `socialMediaId` as a sensitive login credential. Only inspect requests generated by logging in to your own account.

If you cannot find the request, clear the Network filter, enable Preserve log and repeat the login. The portal's internal authentication process may change.

## Entities and historical statistics

The integration discovers linked contracts and creates a device for each one. Entity IDs are assigned by Home Assistant and can vary if you rename a device or entity.

| Entity or data | What it represents |
| --- | --- |
| Suministros | Number of linked electricity contracts |
| Medidor | Meter identifier for a contract |
| Último consumo | Consumption reported for the latest reading period, in kWh |
| Última lectura del medidor | Latest cumulative meter reading reported by Edesur; **not** the period consumption |
| Fecha de última lectura | Date of the latest reading |
| Importe de última factura | Latest invoice amount in ARS |
| Emisión de última factura | Invoice issue date |
| Primer / Segundo vencimiento | Due dates of the latest invoice |
| Último pago / Fecha del último pago | Latest recorded payment amount and date |
| Estado del suministro | Status returned by Edesur |
| Estado de deuda | `Sin deuda registrada`, `Deuda registrada` or unknown, based on the debt API |
| Estado del convenio | Current payment agreement status, when available |
| Estado / Fecha del último trámite | Latest reported customer formality |

### Consumption history

Historical readings are also imported into Home Assistant Recorder as external long-term statistics, with IDs following `edesur:consumption_<contractAccount>`. You can add these IDs to a **Statistics Graph** card with `period: month` and `stat_types: [mean]`.

These observations are **kWh per Edesur reading period**, associated with the month of their reading date. They are **not** real-time measurements, cumulative energy totals, or necessarily calendar-month consumption. The native History dialog for a sensor may not display these external statistic IDs because they are not separate sensor entities. The latest consumption sensor can also expose recent readings through its `history` attribute.

## Updating an existing installation

1. Back up your Home Assistant configuration.
2. Update the integration files through HACS or replace the files manually, according to your installation method.
3. Restart Home Assistant to load the updated Python code.
4. Confirm the existing Edesur integration, devices, sensors and dashboard cards still work.

**Do not delete and re-add the integration just to update it.** Keeping the existing config entry preserves its entity unique IDs and avoids breaking dashboard references.

## Limitations

- Experimental unofficial API; availability, payloads and authentication behavior can change.
- Google/social ID login and standard Edesur password login are implemented; the password endpoint's successful response format still needs live verification. Automatic Google OAuth is not supported.
- Debt status is **not proof that a particular invoice was paid**. Invoice/payment matching, outstanding balance and overdue amount cannot be reliably inferred from the latest invoice and payment.
- Optional debt, agreement and formality endpoints may be unavailable for some accounts.
- Historical statistics are observations assigned to reading dates, not a reconstructed hourly or daily electricity-usage series.
- `activeReading` is the meter's cumulative reading; its exact unit/semantics should be checked against the provider's meter data before treating it as an energy consumption sensor.
- The integration does not currently provide a dedicated diagnostics download or user-configurable refresh interval.
- No payment, contract or supply-control actions are supported.

## Privacy and security

The configuration form masks `socialMediaId` while you enter it; this does **not** encrypt the value at rest. The account email and selected login credential (`socialMediaId` or password) are stored in the Home Assistant configuration entry; Edesur session tokens are held in memory by the API client. Keep your Home Assistant backups, `.storage` directory and network captures private. Never open public issues containing real contract numbers, meter numbers, credentials, social IDs or API tokens.

## Development

GitHub Actions runs unit tests, critical Ruff checks, Python compilation, Hassfest, and HACS validation on pushes and pull requests. All validation jobs run for this public repository. A successful CI run does not guarantee that the unofficial Edesur API will remain compatible.

The `dev` branch is used for ongoing development and testing. The `main` branch is reserved for reviewed, stable changes. Do not assume a change in `dev` has been released.

Bug reports and contributions are welcome through [GitHub Issues](https://github.com/ImNotThrasher/ha-edesur/issues). API research and sanitized Postman resources, where available, are in [docs](docs/). Avoid sharing personal data in bug reports.

## License and trademarks

Licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See [LICENSE](LICENSE).

**Edesur** and related names and logos are the property of their respective owners. This independent project is not affiliated with, endorsed by, sponsored by, or officially supported by Edesur. References are solely for identification and compatibility.
