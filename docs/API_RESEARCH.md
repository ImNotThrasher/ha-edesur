# Investigación de la API de Edesur

La colección de Postman consolidada es la fuente de referencia: `docs/postman/Edesur.postman_collection.json`.

## Autenticación
- Método utilizado por el propietario: Google/social login.
- POST observado: `/Usuario/login-social-media`, campos `socialMediaEmail` y `socialMediaId`.
- Respuesta esperada: objeto JSON con `token`, utilizado como Bearer.
- El POST funciona en el flujo observado. **Pendiente:** obtener `socialMediaId` mediante un mecanismo adecuado dentro de Home Assistant; no se ha implementado OAuth.
- Usuario/contraseña: alternativa conocida en el portal, pero sin documentación del endpoint. No implementada.

## Descubrimiento y consulta
- `GET /Cliente/supply-retrieve/{email}`: respuesta `supplies[]` con `contractAccount`.
- `GET /Cliente/get-client/{contractAccount}`: detalle con `meterNumber`.
- `GET /Cliente/get-historical-readings/{contractAccount}`
- `GET /Cliente/get-historical-invoices/{contractAccount}`
- `GET /Cliente/get-historical-payments/{contractAccount}`
- `GET /Cliente/get-cut-supply/{contractAccount}`
- `POST /PlanPagos/GetDeudaAsync`: método inferido; `nroSuministro` no necesariamente equivale a `contractAccount`.

## Pruebas en Postman
1. Importar la colección y configurar variables **localmente**, nunca subir secretos al repositorio.
2. Configurar `social_email` y `social_id` con los valores propios; no compartir el ID social.
3. Ejecutar la carpeta de autenticación.
4. Ejecutar descubrimiento; comprobar `account_ids` y `client_id`.
5. Consultar detalle e historial; repetir para cada cuenta cambiando `client_id`.
6. Ejecutar deuda **solo** tras validar `supply_number` y el método HTTP.

La colección comprueba códigos HTTP y la presencia de estructuras mínimas, no el significado de cada campo histórico. Guardar ejemplos de respuestas solo después de anonimizar datos personales.

## Decisiones de mantenimiento
- La capa API centraliza endpoints y errores.
- El coordinador consulta contratos en cada actualización; hasta conocer el TTL del token, reautentica en cada ciclo.
- Los sensores solo muestran datos con estructura conocida: cantidad de contratos y número de medidor.
- No hay sensores monetarios ni de consumo hasta validar unidades, fechas y formatos.
- La colección no almacena contraseñas, tokens ni datos personales.

## Validated response fields and deferred mappings (2026-11)

Observed fields: `get-client` returns `meterNumber`, `groupClient`, `electrodependent`, `socialRate` and address; readings contain `readings[]` with `activeConsumption`, `activeReading`, `readingDate`, `remainingConsumption` and time-of-use fields; invoices contain `invoices[]` with `totalAmount`, `issueDate`, `firstDueDate`, `secondDueDate`, `number`, `invoiceAccess`; payments contain `payments[]` with `amount`, `paymentDate`, `paymentTipe`, `entity`; supply status contains `status` (observed: `Con Suministro`).

Implemented: latest active consumption, latest cumulative active reading, last reading date, last invoice amount and dates, last payment amount and date, and raw supply status. Invoice number and payment method are limited attributes. The invoice access URL is intentionally not exposed because it contains an access token.

**Pending verification:**
- `PlanPagos/GetDeudaAsync` returned `successful: false` and `ValorBusqueda` validation error. The endpoint expects a `supply_number` whose derivation and relationship to `contractAccount` are unknown; HTTP method and request schema also need confirmation. Do not generate or guess identifiers.
- Debt, unpaid invoice status, overdue amounts and account balance cannot be derived safely from invoice totals, due dates and payment history alone. Wait for a validated authoritative debt/status response.
- `activeConsumption` is confirmed as period consumption in kWh; it is not a monotonically increasing meter total. `activeReading` still needs independent confirmation before assigning its unit or statistics semantics.
- `remainingConsumption`, `activeConsumptionHP`, `activeConsumptionNight`, `nightReading`, `peakReading`, `remainingReading` require business-semantic verification before mapping.
- Full historical series, tariff group, social rate and electrodependence metadata may be exposed later after reviewing privacy and appropriate entity models.

Never commit raw API response examples containing customer names, addresses, invoice download URLs, or authentication values.

## Additional observed endpoints (2026-11)

- `GET /PlanPagos/get-debts?contractAccount={account}&serchType=1&value={account}`: observed `{ "message": "Al día de la fecha, su cuenta no posee deuda.", "debts": null }`. This is authoritative for no debt at query time, not proof of an individual invoice payment. Nonempty debt list is treated as debt present; amount/structure not validated. Legacy `GetDeudaAsync` retained only for research.
- `GET /Cliente/get-formalities/{account}`: `{ "formalities": [{ "attentionType": "Requerimiento", "status": "ESTA007", "openingDate": "...", "closingDate": "...", "caseNumber": "...", "reason": "Comercial", "subReason": "Adhesión a E-Factura Digital", "statusDescription": "Cerrado", "claimNumber": null, "reasonCode": "MOT003", "subReasonCode": "ATAR183" }] }`. Only latest status/date and minimal case metadata exposed.
- Last payment vs last invoice equality is not a validated paid indicator. Never infer paid status from matching amounts or elapsed due dates.
- Historical consumption is available as a limited `history` attribute on latest-consumption sensor; do not interpret zero as missing without evidence.

## Payment agreements (2026-11)

Observed `GET /PlanPagos/retrieve-agreement/{contractAccount}` with `agreements[]` (historical) and `current` (active agreement or other state). Observed fields: `type`, `state`, `advance`, `currentDebt`, `applicationNumber`, `numberInstallments`, `openingDate`, `closingDate`, `url`, `barCode`. An example `current.state` was `Vigente`, while historical states included `Cancelado` and `Quitado`. Do not equate `currentDebt` with overdue account debt; verify semantics. Do not expose `url`, `barCode` or customer-specific application identifiers in logs, diagnostics, or public docs. This endpoint is in Postman for testing; no Home Assistant entities are implemented yet.
