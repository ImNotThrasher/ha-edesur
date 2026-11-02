# Edesur for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom%20repository-blue.svg)](https://www.hacs.xyz/)

**Unofficial, community-maintained Home Assistant integration** for Edesur Argentina.

Edesur (Empresa Distribuidora de Energía Sur Sociedad Anónima) is a private company providing the public service of electricity distribution and commercialization in Argentina. This integration aims to make information about your Edesur electricity accounts available in Home Assistant.

> [!IMPORTANT]
> This project is **not an official Edesur integration** and is not developed, endorsed, supported, or affiliated with Edesur. It uses an undocumented API that may change without notice.
>
> **Development status:** experimental. The integration has not yet been validated on a running Home Assistant installation.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Entities](#entities)
- [Limitations](#limitations)
- [Privacy and security](#privacy-and-security)
- [Contributing](#contributing)
- [License](#license)

## Features

Currently implemented in code (pending real-world validation):

- Google/social account login using a manually supplied Edesur social identifier.
- Automatic discovery of multiple electricity contracts linked to an account.
- Periodic refresh of account data.
- Basic sensors for linked contracts and meter numbers.

Planned features include historical electricity readings, invoices, payments, outstanding balances, due dates, and supply status. These are **not yet available as Home Assistant entities**.

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

The initial version defines:

| Entity | Description |
| --- | --- |
| Linked contracts | Number of contracts associated with the account |
| Meter number | Meter identifier for each discovered contract, when available |

Additional data may be fetched internally for research, but is not exposed as entities yet.

## Limitations

- **Experimental:** installation, authentication, and sensors still require testing in Home Assistant.
- Only the manual Google/social identifier method is implemented; email/password login is not supported.
- Edesur's undocumented API can change or become unavailable.
- The integration does not control electricity supply, make payments, or modify account details.
- Historical readings, invoices, payments, debt, and due-date sensors are not implemented yet.

## Privacy and security

The integration communicates with Edesur to access the account information required for its sensors. Your email and social identifier are stored in Home Assistant's integration configuration; the session token is kept in memory by the API client. Treat your Home Assistant backups as sensitive.

This is an independent, unofficial project. Use it at your own risk.

## Contributing

Bug reports and contributions are welcome through [GitHub Issues](https://github.com/ImNotThrasher/ha-edesur/issues). Technical API research and the sanitized Postman collection are available in [docs](docs/).

## License

Distributed under the [GNU General Public License v3.0](LICENSE).
