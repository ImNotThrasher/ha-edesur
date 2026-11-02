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
